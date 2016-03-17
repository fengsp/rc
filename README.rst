rc
==

.. image:: https://github.com/fengsp/rc/blob/master/docs/_static/rc.png?raw=true
   :alt: rc: the redis cache

rc - the redis cache.

- easy to use
- can build cache cluster
- batch-fetch multiple cache results (do it in parallel for cluster)

For full documentation see `rc.readthedocs.org <http://rc.readthedocs.org/>`_.


Installation
------------

.. code-block:: bash
    
    $ pip install rc


Quickstart
----------

A minimal cache example looks like this:

.. code-block:: python

    from rc import Cache

    cache = Cache()
    assert cache.set('key', 'value')
    assert cache.get('key') == 'value'
    assert cache.get('foo') is None
    assert cache.set('list', [1])
    assert cache.get('list') == [1]

A cache cluster use a redis cluster as backend:

.. code-block:: python

    from rc import CacheCluster

    cache = CacheCluster({
        'cache01': {'host': 'redis-host01'},
        'cache02': {'host': 'redis-host02'},
        'cache03': {'host': 'redis-host03'},
        'cache04': {'host': 'redis-host04', 'db': 1},
    })

Cache decorator:

.. code-block:: python

    @cache.cache()
    def load(name, offset):
        return load_from_database(name, offset)

    rv = load('name', offset=10)

Batch fetch multiple cache results:

.. code-block:: python

    assert cache.get_many('key', 'foo') == ['value', None]

    # for cache decorated function
    @cache.cache()
    def cached_func(param):
        return param

    results = []
    # with the context manager, the function
    # is executed and return a promise
    with cache.batch_mode():
        for i in range(10):
            results.append(cached_func(i))
    for i, rv in enumerate(results):
        assert rv.value == i

Cache invalidation:

.. code-block:: python

    cache.delete('key')
    # for decorated function
    cache.invalidate(load, 'name', offset=10)


Better
------

If you feel anything wrong, feedbacks or pull requests are welcome.
