.. _cache:

Cache
=====

This page gives you some details on caching.


Create Cache Object
-------------------

Keep one cache instance around so we can do caching easily.  There are two
types of cache in RC, if you are building a small project and one redis server
is enough to hold your cache, go with :class:`~rc.Cache`, if you are working
on a website that is accessed millions of times per day,
:class:`~rc.CacheCluster` is the ideal solution.


Cache Global Namespace
----------------------

Namespace is a global thing with one cache object.  All cache object can have
a namespace, by default, it is not set.  The idea is simple, namespace is just
one prefix that will be added to all keys set through this cache object.
You can use this to distinguist usage A from usage B if you are sharing
redis server resources on them.  There is a parameter that is used to set
this up, a simple demo::

    from rc import Cache

    models_cache = Cache(namespace='models')
    templates_cache = Cache(namespace='templates')


Cache Function Result
---------------------

There is one useful decorator api used to cache result for a function,
check out :meth:`~rc.cache.BaseCache.cache`.  Here is a simple example::

    from rc import Cache

    cache = Cache()

    @cache.cache()
    def load(name, offset):
        return load_from_database(name, offset)

    rv = load('name', 10)

If you have two functions with same name inside one module, use `key_prefix`
to distinguish them::

    class Data(object):
        @cache.cache(key_prefix='another')
        def load(self, name, offset):
            return load_from_another_place(name, offset)


Cache Expiration Time
---------------------

The cache expires automatically in time seconds, there is one `default_expire`
that is used for all set on a cache object::

    cache = Cache(default_expire=24 * 3600)  # one day

Of course you can change it on every cache set::

    cache.set('key', 'value', expire=3600)  # one hour


Cache Invalidation
------------------

For a cache key that is set manually by you, simplily delete it::

    cache.delete('key')

In order to invalidate a cached function with certain arguments::

    @cache.cache()
    def load(name, offset):
        return load_from_database(name, offset)

    rv = load('name', offset=10)

    # always invalidate using the same positional and keyword parameters
    # as you call the function
    cache.invalidate(load, 'name', offset=10)

What if you want to expire all results of this function with any parameters,
since we have a `key_prefix`, just change it to a different value, like from
``'version01'`` to ``'version02'``, the data of old version wouldn't be
deleted immediately, however, they are going to be pushed out after
expiration time.


Cache Batch Fetching
--------------------

- how to do batch fetch
- how it is done for a cache
- for a cache cluster we do it in parallel
