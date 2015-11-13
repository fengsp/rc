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

What we are doing here?

1. First we imported the :class:`~rc.Cache` class.  An instance of this class
   can be used to cache things with a single redis server.
2. pass


Build A Cache Cluster
---------------------

::

    pass


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

    pass


Cache Invalidation
------------------

::

    cache.delete('key')
    # for decorated function
    cache.invalidate(load, 'name', offset=10)
