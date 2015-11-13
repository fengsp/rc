.. _cache_config:

Cache Config
============

This page gives you introductions on creating a :class:`~rc.Cache` instance.


Basic Config
------------

Cache takes parameters for basic redis server setup and cache setup.  Here is
one simple demo::

    from rc import Cache

    cache = Cache('redishost01', 6379, db=0, password='pass',
                  socket_timeout=5)

There are other parameters you can config, you can specify your own customized
serializer_cls, you can change default expiration time to any length you want,
you can set a namespace for this cache instance, for more details, check out
:class:`~rc.Cache`.


Redis Options
-------------

There is one parameter called ``redis_options``, you can use this to set
other parameters to the underlying :class:`redis.StrictRedis`.  Here is a
simple example::

    from rc import Cache

    cache = Cache(redis_options={'unix_socket_path': '/tmp/redis.sock'})
