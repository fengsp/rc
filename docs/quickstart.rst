.. _quickstart:

Quickstart
==========

This page gives a introduction to RC.


A Simple Example
----------------

A minimal cache example looks like this::

    from rc import Cache

    c = Cache()
    c.set('key', 'value')
    assert c.get('key') == 'value'
    assert c.get('foo') is None

What we are doing here?

1. First we imported the :class:`~rc.Cache` class.  An instance of this class
   can be used to cache things with a single redis server.
2. pass


Build A Cache Cluster
---------------------

pass


Cache Decorator
---------------

pass


Batch Fetch Multiple Cache Results
----------------------------------

pass


Cache Invalidation
------------------

pass
