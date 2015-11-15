# -*- coding: utf-8 -*-
import socket
import errno
from itertools import izip

from redis import StrictRedis
from redis.client import list_or_args
from redis.exceptions import ConnectionError
try:
    from redis.exceptions import TimeoutError
except ImportError:
    TimeoutError = ConnectionError

from rc.poller import poller


class BaseRedisClient(StrictRedis):
    pass


class RedisClient(BaseRedisClient):
    pass


class RedisClusterClient(BaseRedisClient):

    def __init__(self, connection_pool, max_concurrency=64,
                 poller_timeout=1.0):
        BaseRedisClient.__init__(self, connection_pool=connection_pool)
        self.max_concurrency = max_concurrency
        self.poller_timeout = poller_timeout

    def execute_command(self, *args, **options):
        command_name = args[0]
        command_args = args[1:]
        connection_pool = self.connection_pool
        router = connection_pool.cluster.router
        host_name = router.get_host_for_command(command_name, command_args)
        connection = connection_pool.get_connection(command_name, host_name)
        try:
            connection.send_command(*args)
            return self.parse_response(connection, command_name, **options)
        except (ConnectionError, TimeoutError) as e:
            connection.disconnect()
            if not connection.retry_on_timeout and isinstance(e, TimeoutError):
                raise
            connection.send_command(*args)
            return self.parse_response(connection, command_name, **options)
        finally:
            connection_pool.release(connection)

    def delete(self, name):
        """We just support one key delete for now."""
        names = [name]
        return self.execute_command('DEL', *names)

    def mdelete(self, *names):
        commands = []
        for name in names:
            commands.append(('DEL', name))
        results = self._execute_multi_command_with_poller('DEL', commands)
        return sum(results.values())

    def msetex(self, mapping, time):
        commands = []
        for name, value in mapping.iteritems():
            commands.append(('SETEX', name, time, value))
        results = self._execute_multi_command_with_poller('SETEX', commands)
        return all(results.values())

    def mget(self, keys, *args):
        args = list_or_args(keys, args)
        commands = []
        for arg in args:
            commands.append(('MGET', arg))
        results = self._execute_multi_command_with_poller('MGET', commands)
        return [results[k] for k in args]

    def _execute_multi_command_with_poller(self, command_name, commands):
        connection_pool = self.connection_pool
        router = connection_pool.cluster.router
        # put command to the corresponding command buffer
        bufs = {}
        for args in commands:
            host_name = router.get_host_for_key(args[1])
            buf = self._get_command_buffer(bufs, command_name, host_name)
            buf.enqueue_command(args)
        # poll all results back with max concurrency
        results = {}
        remaining_buf_items = bufs.items()
        while remaining_buf_items:
            buf_items = remaining_buf_items[:self.max_concurrency]
            remaining_buf_items = remaining_buf_items[self.max_concurrency:]
            bufs_poll = poller(buf_items)
            while bufs_poll:
                rlist, wlist = bufs_poll.poll(self.poller_timeout)
                for rbuf in rlist:
                    if not rbuf.has_pending_request:
                        results.update(rbuf.fetch_response(self))
                        bufs_poll.pop(rbuf.host_name)
                for wbuf in wlist:
                    if wbuf.has_pending_request:
                        wbuf.send_pending_request()
        # clean
        for _, buf in bufs.iteritems():
            connection_pool.release(buf.connection)
        return results

    def _get_command_buffer(self, bufs, command_name, host_name):
        buf = bufs.get(host_name)
        if buf is not None:
            return buf
        connection_pool = self.connection_pool
        connection = connection_pool.get_connection(command_name, host_name)
        buf = CommandBuffer(host_name, connection, command_name)
        bufs[host_name] = buf
        return buf


class CommandBuffer(object):
    """The command buffer is used for sending and fetching multi key command
    related data.
    """

    def __init__(self, host_name, connection, command_name):
        self.host_name = host_name
        self.connection = connection
        self.command_name = command_name
        self.commands = []
        self.pending_commands = []
        self._send_buf = []

        connection.connect()

    def assert_open(self):
        if self.connection._sock is None:
            raise ValueError('Can not operate on closed file.')

    def enqueue_command(self, command):
        self.commands.append(command)

    def fileno(self):
        self.assert_open()
        return self.connection._sock.fileno()

    @property
    def has_pending_request(self):
        return self._send_buf or self.commands

    def _try_send_buffer(self):
        sock = self.connection._sock
        try:
            timeout = sock.gettimeout()
            sock.setblocking(False)
            try:
                for i, item in enumerate(self._send_buf):
                    sent = 0
                    while 1:
                        try:
                            sent = sock.send(item)
                        except socket.error, e:
                            if e.errno == errno.EAGAIN:
                                continue
                            elif e.errno == errno.EWOULDBLOCK:
                                break
                            raise
                        break
                    if sent < len(item):
                        self._send_buf[:i + 1] = [item[sent:]]
                        break
                else:
                    del self._send_buf[:]
            finally:
                sock.settimeout(timeout)
        except socket.timeout:
            self.connection.disconnect()
            raise TimeoutError('Timeout writing to socket (%s)'
                               % self.host_name)
        except socket.error:
            self.connection.disconnect()
            raise ConnectionError('Error while writing to socket (%s)'
                                  % self.host_name)
        except:
            self.connection.disconnect()
            raise

    def batch_commands(self, commands):
        args = []
        for command in commands:
            command_args = command[1:]
            args.extend(command_args)
        if args:
            return [(self.command_name,) + tuple(args)]
        else:
            return []

    def send_pending_request(self):
        self.assert_open()
        if self.commands:
            if self.command_name in ('MGET', 'DEL'):
                commands = self.batch_commands(self.commands)
            else:
                commands = self.commands
            self._send_buf.extend(self.connection.pack_commands(commands))
            self.pending_commands = self.commands
            self.commands = []
        if not self._send_buf:
            return True
        self._try_send_buffer()
        return not self._send_buf

    def fetch_response(self, client):
        self.assert_open()
        if self.has_pending_request:
            raise RuntimeError('There are pending requests.')
        if self.command_name in ('MGET', 'DEL'):
            rv = client.parse_response(self.connection, self.command_name)
        else:
            rv = []
            for i in xrange(len(self.pending_commands)):
                rv.append(client.parse_response(
                    self.connection, self.command_name))
        if self.command_name == 'DEL':
            rv = [1] * rv + [0] * (len(self.pending_commands) - rv)
        pending_keys = map(lambda c: c[1], self.pending_commands)
        return dict(izip(pending_keys, rv))
