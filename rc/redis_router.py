# -*- coding: utf-8 -*-
from binascii import crc32

from rc.ketama import HashRing


class BaseRedisRouter(object):
    """Subclass this to implement your own router."""

    def __init__(self, hosts):
        self.hosts = hosts

    def get_key_for_command(self, command, args):
        if command in ('GET', 'SET', 'SETEX', 'DEL'):
            return args[0]
        raise RuntimeError('The command "%s" is not supported yet.' % command)

    def get_host_for_key(self, key):
        """Get host name for a certain key."""
        raise NotImplementedError()

    def get_host_for_command(self, command, args):
        return self.get_host_for_key(self.get_key_for_command(command, args))


class RedisCRC32HashRouter(BaseRedisRouter):
    """Use crc32 for hash partitioning."""

    def __init__(self, hosts):
        BaseRedisRouter.__init__(self, hosts)
        self._sorted_host_names = sorted(hosts.keys())

    def get_host_for_key(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        else:
            key = str(key)
        pos = crc32(key) % len(self._sorted_host_names)
        return self._sorted_host_names[pos]


class RedisConsistentHashRouter(BaseRedisRouter):
    """Use ketama for hash partitioning."""

    def __init__(self, hosts):
        BaseRedisRouter.__init__(self, hosts)
        self._hashring = HashRing(hosts.values())

    def get_host_for_key(self, key):
        node = self._hashring.get_node(key)
        if node is None:
            raise RuntimeError('Can not find a host using consistent hash')
        return node.host_name
