import socket
import errno

from redis import StrictRedis
from redis.client import list_or_args
from redis.exceptions import ConnectionError
try:
    from redis.exceptions import TimeoutError
except ImportError:
    TimeoutError = ConnectionError

from rc.poller import poller


class RedisBaseClient(StrictRedis):
    pass


class RedisClient(RedisBaseClient):
    pass


class RedisClusterClient(RedisBaseClient):

    def __init__(self, connection_pool, max_concurrency=None):
        RedisBaseClient.__init__(self, connection_pool=connection_pool)
        if max_concurrency is None:
            max_concurrency = 64
        self.max_concurrency = max_concurrency

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

    def mget(self, keys, *args):
        args = list_or_args(keys, args)
        connection_pool = self.connection_pool
        router = connection_pool.cluster.router
        # put keys to the corresponding mget buffer
        bufs = {}
        for arg in args:
            host_name = router.get_host_for_key(arg)
            buf = self._get_mget_buffer(bufs, host_name)
            buf.enqueue_key(arg)
        # poll all results back with max concurrency
        results = {}
        remaining_buf_items = bufs.items()
        while remaining_buf_items:
            buf_items = remaining_buf_items[:self.max_concurrency]
            remaining_buf_items = remaining_buf_items[self.max_concurrency:]
            bufs_poll = poller(buf_items)
            while bufs_poll:
                rlist, wlist = bufs_poll.poll()
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
        return [results[k] for k in args]

    def _get_mget_buffer(self, bufs, host_name):
        buf = bufs.get(host_name)
        if buf is not None:
            return buf
        connection_pool = self.connection_pool
        connection = connection_pool.get_connection('MGET', host_name)
        buf = MGETBuffer(host_name, connection)
        bufs[host_name] = buf
        return buf


class MGETBuffer(object):
    """The mget buffer is used for sending and fetching MGET command related
    data.
    """

    def __init__(self, host_name, connection):
        self.host_name = host_name
        self.connection = connection
        self.keys = []
        self.pending_keys = []
        self._send_buf = []

        connection.connect()

    def assert_open(self):
        if self.connection._sock is None:
            raise ValueError('Can not operate on closed file.')

    def enqueue_key(self, key):
        self.keys.append(key)

    def fileno(self):
        self.assert_open()
        return self.connection._sock.fileno()

    @property
    def has_pending_request(self):
        return self._send_buf or self.keys

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

    def send_pending_request(self):
        self.assert_open()
        if self.keys:
            args = ('MGET',) + tuple(self.keys)
            self._send_buf.extend(self.connection.pack_command(*args))
            self.pending_keys = self.keys
            self.keys = []
        if not self._send_buf:
            return True
        self._try_send_buffer()
        return not self._send_buf

    def fetch_response(self, client):
        self.assert_open()
        if self.has_pending_request:
            raise RuntimeError('There are pending requests.')
        rv = client.parse_response(self.connection, 'MGET')
        return dict(zip(self.pending_keys, rv))
