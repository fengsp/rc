.. _foreword:

Foreword
========

Read this before you get started if you are not familiar with cache.


Why
---

Speed.  The main problem with many applications is, they're slow.  Each time
we get the result, a lot of code are executed.  And cache is the easiest way
to speed up things.  If you are serious about performance, use more caching.


How Caching Works
-----------------

What does a cache do?  Imagine we have a function that takes some time to
complete, the idea is that we put the result of that expensive operation into
a cache for some time.

Basically we have a cache object that is connected to a remote server or file
system or memory.  When the request comes in, you check if the result is
in the cache, if so, you return it from the cache.  Otherwise you execute the
calculation and put it in the cache.

Here is a simple example::

    def get_result():
        rv = cache.get('mykey')
        if rv is None:
            rv = calculate_result()
            cache.set('mykey', rv)
        return rv
