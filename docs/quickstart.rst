.. _quickstart:

Quickstart
==========

This page gives a introduction to RC.


A Simple Example
----------------

A minimal cache example looks like this::

    from rc import Cache

    cache = Cache()
    assert cache.set('key', 'value')
    assert cache.get('key') == 'value'
    assert cache.get('foo') is None
    assert cache.set('list', [1])
    assert cache.get('list') == [1]

What we are doing here?

1. First we imported the :class:`~rc.Cache` class.  An instance of this class
   can be used to cache things with a single redis server.
2. We create one cache instance.
3. We set and get things based on a key.


Build A Cache Cluster
---------------------

A cache cluster use a redis cluster as backend.

::

    from rc import CacheCluster

    cache = CacheCluster({
        'cache01': {'host': 'redis-host01'},
        'cache02': {'host': 'redis-host02'},
        'cache03': {'host': 'redis-host03'},
        'cache04': {'host': 'redis-host04', 'db': 1},
    })


Cache Decorator
---------------

::

    @cache.cache()
    def load(name, offset):
        return load_from_database(name, offset)

    rv = load('name', offset=10)


Batch Fetch Multiple Cache Results
----------------------------------

::

    assert cache.get_many('key', 'foo') == ['value', None]
    # for decorated function
    pass


Cache Invalidation
------------------

::

    cache.delete('key')
    # for decorated function
    cache.invalidate(load, 'name', offset=10)
