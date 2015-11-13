# -*- coding: utf-8 -*-
import functools

from rc.redis_clients import RedisClient
from rc.redis_cluster import RedisCluster
from rc.serializer import JSONSerializer
from rc.utils import generate_key_for_cached_func


class cached_property(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype):
        rv = obj.__dict__[self.fget.__name__] = self.fget(obj)
        return rv


class BaseCache(object):
    """Baseclass for all redis cache systems.

    :param namespace: a prefix that should be added to all keys
    :param serializer_cls: the serialization class you want to use.
    :param default_expire: default expiration time that is used if no
                           expire specified on :meth:`set`.
    """

    def __init__(self, namespace=None, serializer_cls=None,
                 default_expire=3 * 24 * 3600):
        if serializer_cls is None:
            serializer_cls = JSONSerializer
        self.namespace = namespace or ''
        self.serializer_cls = serializer_cls
        self.default_expire = default_expire

    def get_client(self):
        """Returns the redis client that is used for cache."""
        raise NotImplementedError()

    @cached_property
    def client(self):
        """Returns the redis client that is used for cache."""
        return self.get_client()

    @cached_property
    def serializer(self):
        """Returns the serializer instance that is used for cache."""
        return self.serializer_cls()

    def get(self, key):
        """Returns the value for the cache key, otherwise `None` is returned.

        :param key: cache key
        """
        return self.serializer.loads(self.client.get(self.namespace + key))

    def set(self, key, value, expire=None):
        """Adds or overwrites key/value to the cache.   The value expires in
        time seconds.

        :param key: cache key
        :param value: value for the key
        :param expire: expiration time
        :return: Whether the key has been set
        """
        if expire is None:
            expire = self.default_expire
        string = self.serializer.dumps(value)
        return self.client.setex(self.namespace + key, expire, string)

    def delete(self, key):
        """Deletes the value for the cache key.

        :param key: cache key
        :return: Whether the key has been deleted
        """
        return self.client.delete(self.namespace + key)

    def get_many(self, *keys):
        """Returns the a list of values for the cache keys."""
        if self.namespace:
            keys = [self.namespace + key for key in keys]
        return [self.serializer.loads(s) for s in self.client.mget(keys)]

    def set_many(self, mapping, expire=None):
        """Sets multiple keys and values using dictionary.
        The values expires in time seconds.

        :param mapping: a dictionary with key/values to set
        :param expire: expiration time
        :return: whether all keys has been set
        """
        rv = True
        for key, value in mapping.iteritems():
            if not self.set(key, value, expire):
                rv = False
        return rv

    def delete_many(self, *keys):
        """Deletes multiple keys.

        :return: whether all keys has been deleted
        """
        return all(self.delete(key) for key in keys)

    def cache(self, key_prefix=None, expire=None):
        """A decorator that is used to cache a function with supplied
        parameters.  It is intended for decorator usage::

            @cache.cache()
            def load(name):
                return load_from_database(name)

            rv = load('foo')
            rv = load('foo') # returned from cache

        The cache key doesn't need to be specified, it will be created with
        the name of the module + the name of the function + function arguments.

        :param key_prefix: this is used to ensure cache result won't clash
                           with another function that has the same name
                           in this module, normally you do not need to pass
                           this in
        :param expire: expiration time

        .. note::

            The function being decorated must be called with the same
            positional and keyword arguments.  Otherwise, you might create
            multiple caches.  If you pass one parameter as positional, do it
            always.

        .. note::

            When a method on a class is decorated, the ``self`` or ``cls``
            arguments is not included in the cache key.
        """
        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                cache_key = generate_key_for_cached_func(
                    key_prefix, f, *args, **kwargs)
                rv = self.get(cache_key)
                if rv is not None:
                    return rv
                rv = f(*args, **kwargs)
                self.set(cache_key, rv, expire)
                return rv

            wrapper.__rc_cache_params__ = {
                'key_prefix': key_prefix,
                'expire': expire,
            }
            return wrapper
        return decorator

    def invalidate(self, func, *args, **kwargs):
        """Invalidate a cache decorated function.  You must call this with
        the same positional and keyword arguments as what you did when you
        call the decorated function, otherwise the cache will not be deleted.
        The usage is simple::

            @cache.cache()
            def load(name, limit):
                return load_from_database(name, limit)

            rv = load('foo', limit=5)

            cache.invalidate(load, 'foo', limit=5)

        :param func: decorated function to invalidate
        :param args: same positional arguments as you call the function
        :param kwargs: same keyword arguments as you call the function
        :return: whether it is invalidated or not
        """
        try:
            cache_params = func.__rc_cache_params__
        except AttributeError:
            raise TypeError('Attempted to invalidate a function that is'
                            'not cache decorated')
        key_prefix = cache_params['key_prefix']
        cache_key = generate_key_for_cached_func(
            key_prefix, func, *args, **kwargs)
        return self.delete(cache_key)


class Cache(BaseCache):
    """Uses a single Redis server as backend.

    :param host: address of the Redis, this is compatible with the official
                 Python StrictRedis cilent (redis-py).
    :param port: port number of the Redis server.
    :param db: db numeric index of the Redis server.
    :param password: password authentication for the Redis server.
    :param socket_timeout: socket timeout for the StrictRedis client.
    :param namespace: a prefix that should be added to all keys.
    :param serializer_cls: the serialization class you want to use.
                           By default, it is :class:`rc.JSONSerializer`.
    :param default_expire: default expiration time that is used if no
                           expire specified on :meth:`set`.
    :param redis_options: a dictionary of parameters that are useful for
                          setting other parameters to the StrictRedis client.
    """

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, namespace=None, serializer_cls=None,
                 default_expire=3 * 24 * 3600, redis_options=None):
        BaseCache.__init__(self, namespace, serializer_cls,
                           default_expire)
        if redis_options is None:
            redis_options = {}
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        self.redis_options = redis_options

    def get_client(self):
        return RedisClient(host=self.host, port=self.port, db=self.db,
                           password=self.password,
                           socket_timeout=self.socket_timeout,
                           **self.redis_options)

    def delete_many(self, *keys):
        """Deletes multiple keys.

        :return: whether all keys has been deleted
        """
        if self.namespace:
            keys = [self.namespace + key for key in keys]
        return self.client.delete(*keys)


class CacheCluster(BaseCache):
    """The core object behind rc."""

    def __init__(self):
        pass
