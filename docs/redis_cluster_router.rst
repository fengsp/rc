.. _redis_cluster_router:

Redis Cluster Router
====================

This page gives you introductions on redis router for cluster.


CRC32Hash Router
----------------

Router that just routes commands to redis node based on ``crc32 % node_num``.
For more details check out :class:`~rc.RedisCRC32HashRouter`.


ConsistentHash Router
---------------------

Router that routes to redis based on consistent hashing algorithm.
For more details check out :class:`~rc.RedisConsistentHashRouter`.


Build Your Own Router
---------------------

Subclass :class:`~rc.BaseRedisRouter`, implement
:meth:`~rc.BaseRedisRouter.get_host_for_key`.

Here is the builtin CRC32 router::

    from binascii import crc32


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
