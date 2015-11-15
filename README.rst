RC
==

rc - the redis cache.

- easy to use
- can build cache cluster
- batch-fetch multiple cache results (do it in parallel for cluster)

For full documentation see `rc.readthedocs.org <http://rc.readthedocs.org/>`_.


Installation
------------

::
    
    $ pip install rc


Quickstart
----------

A minimal cache example looks like this::

    from rc import Cache

    cache = Cache()
    assert cache.set('key', 'value')
    assert cache.get('key') == 'value'
    assert cache.get('foo') is None

A cache cluster use a redis cluster as backend::

    from rc import CacheCluster

    cache = CacheCluster({
        'cache01': {'host': 'redis-host01'},
        'cache02': {'host': 'redis-host02'},
        'cache03': {'host': 'redis-host03'},
        'cache04': {'host': 'redis-host04', 'db': 1},
    })

Cache decorator::

    @cache.cache()
    def load(name, offset):
        return load_from_database(name, offset)

    rv = load('name', offset=10)

Batch fetch multiple cache results::

    pass

Cache invalidation::

    cache.delete('key')
    # for decorated function
    cache.invalidate(load, 'name', offset=10)


Better
------

If you feel anything wrong, feedbacks or pull requests are welcomed.
