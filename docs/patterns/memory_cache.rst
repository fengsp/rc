.. _memory_cache:

Cache In Memory
===============

RC doesn't support other backends, because mostly you want to use a cache
server.  But if you really need to put some cache in memory, it should be
easy::

    from functools import wraps

    def cache(func):
        saved = {}
        @wraps(func)
        def newfunc(*args):
            if args in saved:
                return saved[args]
            result = func(*args)
            saved[args] = result
            return result
        return newfunc

    @cache
    def lookup(url):
        return url
