.. _cache_cluster_config:

Cache Cluster Config
====================

This page gives you introductions on how to create a :class:`~rc.CacheCluster`
instance.


Basic Config
------------

Simple demo::

    from rc import CacheCluster

    cache = CacheCluster({
        0: {'host': 'redis-host-01'},
        1: {'host': 'redis-host-02', 'port': 6479},
        2: {'unix_socket_path': '/tmp/redis.sock'},
        3: {'host': 'redis-host-03', 'db': 1},
    })

Basically `hosts` is just one dictionary that maps host name to parameters
which are taken by :class:`~rc.redis_cluster.HostConfig`, excluding
`host_name`.

Just like `Cache`, you can specify your own customized `serializer_cls`,
you can change default expiration time to any length you want, you can set
a namespace for this cache instance, for more details, check out
:class:`~rc.CacheCluster`.


Redis Connection Pool Config
----------------------------

By default we use :class:`~redis.ConnectionPool`, specify your own connection
pool class and options using parameters called ``pool_cls`` and
``pool_options``.


Redis Router Config
-------------------

By default we use :class:`~rc.RedisCRC32HashRouter`, specify your own router
class and options using parameters called ``router_cls`` and
``router_options``.  For more routers, check out :ref:`redis_cluster_router`.


Concurrency Config
------------------

For operations on multiple keys like `get_many`, `set_many` and `delete_many`,
we execute them in parallel.  Under the hood, we does the parallel query using
a select loop(select/poll/kqueue/epoll).  Mostly, if we are using several
remote redis servers, we achieve higher performance.  You can specify
``max_concurrency`` and ``poller_timeout`` to control maximum concurrency and
timeout for poller.
