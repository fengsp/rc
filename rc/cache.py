# -*- coding: utf-8 -*-
import inspect
import functools
from itertools import izip

from rc.redis_clients import RedisClient
from rc.redis_cluster import RedisCluster
from rc.serializer import JSONSerializer
from rc.utils import generate_key_for_cached_func
from rc.promise import Promise


#: Running mode for cache
NORMAL_MODE = 0
BATCH_MODE = 1


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
                           expire specified on :meth:`~rc.cache.BaseCache.set`.
    :param bypass_values: a list of return values that would be ignored by the
                          cache decorator and won't be cached at all.

    .. versionadded:: 0.3
        The `bypass_values` parameter was added.
    """

    def __init__(self, namespace=None, serializer_cls=None,
                 default_expire=3 * 24 * 3600, bypass_values=[]):
        if serializer_cls is None:
            serializer_cls = JSONSerializer
        self.namespace = namespace or ''
        self.serializer_cls = serializer_cls
        self.default_expire = default_expire
        self.bypass_values = bypass_values
        self._running_mode = NORMAL_MODE
        self._pending_operations = []

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

    def _raw_get(self, key):
        return self.client.get(self.namespace + key)

    def _raw_set(self, key, string, expire=None):
        if expire is None:
            expire = self.default_expire
        return self.client.setex(self.namespace + key, expire, string)

    def _raw_get_many(self, *keys):
        if not keys:
            return []
        if self.namespace:
            keys = [self.namespace + key for key in keys]
        return self.client.mget(keys)

    def get(self, key):
        """Returns the value for the cache key, otherwise `None` is returned.

        :param key: cache key
        """
        return self.serializer.loads(self._raw_get(key))

    def set(self, key, value, expire=None):
        """Adds or overwrites key/value to the cache.   The value expires in
        time seconds.

        :param key: cache key
        :param value: value for the key
        :param expire: expiration time
        :return: Whether the key has been set
        """
        return self._raw_set(key, self.serializer.dumps(value), expire)

    def delete(self, key):
        """Deletes the value for the cache key.

        :param key: cache key
        :return: Whether the key has been deleted
        """
        return self.client.delete(self.namespace + key)

    def get_many(self, *keys):
        """Returns the a list of values for the cache keys."""
        return [self.serializer.loads(s) for s in self._raw_get_many(*keys)]

    def set_many(self, mapping, expire=None):
        """Sets multiple keys and values using dictionary.
        The values expires in time seconds.

        :param mapping: a dictionary with key/values to set
        :param expire: expiration time
        :return: whether all keys has been set
        """
        if not mapping:
            return True
        rv = True
        for key, value in mapping.iteritems():
            if not self.set(key, value, expire):
                rv = False
        return rv

    def delete_many(self, *keys):
        """Deletes multiple keys.

        :return: whether all keys has been deleted
        """
        if not keys:
            return True
        return all(self.delete(key) for key in keys)

    def cache(self, key_prefix=None, expire=None, include_self=False):
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
        :param include_self: whether to include the `self` or `cls` as
                             cache key for method or not, default to be False

        .. note::

            The function being decorated must be called with the same
            positional and keyword arguments.  Otherwise, you might create
            multiple caches.  If you pass one parameter as positional, do it
            always.

        .. note::

            Using objects as part of the cache key is possible, though it is
            suggested to not pass in an object instance as parameter.  We
            perform a str() on the passed in objects so that you can provide
            a __str__ function that returns a identifying string for that
            object, the unique string will be used as part of the cache key.

        .. note::

            When a method on a class is decorated, the ``self`` or ``cls``
            arguments is not included in the cache key.  Starting from 0.2
            you can control it with `include_self`.  If you set
            `include_self` to True, remember to provide `__str__` method
            for the object, otherwise you might encounter random behavior.

        .. versionadded:: 0.2
            The `include_self` parameter was added.
        """
        def decorator(f):
            argspec = inspect.getargspec(f)
            if argspec and argspec[0] and argspec[0][0] in ('self', 'cls'):
                has_self = True
            else:
                has_self = False

            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                cache_args = args
                # handle self and cls
                if has_self:
                    if not include_self:
                        cache_args = args[1:]
                cache_key = generate_key_for_cached_func(
                    key_prefix, f, *cache_args, **kwargs)
                if self._running_mode == BATCH_MODE:
                    promise = Promise()
                    self._pending_operations.append(
                        (f, args, kwargs, promise, cache_key, expire))
                    return promise
                rv = self._raw_get(cache_key)
                if rv is None:
                    value = f(*args, **kwargs)
                    rv = self.serializer.dumps(value)
                    if value not in self.bypass_values:
                        self._raw_set(cache_key, rv, expire)
                return self.serializer.loads(rv)

            wrapper.__rc_cache_params__ = {
                'key_prefix': key_prefix,
                'expire': expire,
                'include_self': include_self,
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
        cache_args = args
        include_self = cache_params.get('include_self', False)
        if include_self:
            instance_self = getattr(func, '__self__', None)
            if instance_self:
                cache_args = tuple([instance_self] + list(args))
        cache_key = generate_key_for_cached_func(
            key_prefix, func, *cache_args, **kwargs)
        return self.delete(cache_key)

    def batch_mode(self):
        """Returns a context manager for cache batch mode.  This is used
        to batch fetch results of cache decorated functions.  All results
        returned by cache decorated function will be
        :class:`~rc.promise.Promise` object.  This context manager runs the
        batch fetch and then resolves all promises in the end.  Example::

            results = []
            with cache.batch_mode():
                for i in range(10):
                    results.append(get_result(i))
            results = map(lambda r: r.value, results)

        .. note::

            When you are using rc on this mode, rc is not thread safe.
        """
        return BatchManager(self)

    def batch(self, cancel=False):
        if self._running_mode != BATCH_MODE:
            raise RuntimeError('You have to batch on batch mode.')
        pending_operations = self._pending_operations
        self._pending_operations = []
        self._running_mode = NORMAL_MODE
        if cancel:
            return
        cache_keys = []
        for f, args, kwargs, promise, cache_key, expire in pending_operations:
            cache_keys.append(cache_key)
        cache_results = self._raw_get_many(*cache_keys)
        for rv, (func, args, kwargs, promise, cache_key, expire) in izip(
                cache_results, pending_operations):
            if rv is None:
                value = func(*args, **kwargs)
                rv = self.serializer.dumps(value)
                if value not in self.bypass_values:
                    self._raw_set(cache_key, rv, expire)
            promise.resolve(self.serializer.loads(rv))


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
    :param bypass_values: a list of return values that would be ignored by the
                          cache decorator and won't be cached at all.

    .. versionadded:: 0.3
        The `bypass_values` parameter was added.
    """

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, namespace=None, serializer_cls=None,
                 default_expire=3 * 24 * 3600, redis_options=None,
                 bypass_values=[]):
        BaseCache.__init__(self, namespace, serializer_cls, default_expire,
                           bypass_values)
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

    def set_many(self, mapping, expire=None):
        if not mapping:
            return True
        if expire is None:
            expire = self.default_expire
        pipe = self.client.pipeline()
        for key, value in mapping.iteritems():
            string = self.serializer.dumps(value)
            pipe.setex(self.namespace + key, expire, string)
        return all(pipe.execute())

    def delete_many(self, *keys):
        if not keys:
            return True
        if self.namespace:
            keys = [self.namespace + key for key in keys]
        return self.client.delete(*keys)


class CacheCluster(BaseCache):
    """The a redis cluster as backend.

    Basic example::

        cache = CacheCluster({
            0: {'port': 6379},
            1: {'port': 6479},
            2: {'port': 6579},
            3: {'port': 6679},
        })

    :param hosts: a dictionary of hosts that maps the host host_name to
                  configuration parameters.  The parameters are used to
                  construct a :class:`~rc.redis_cluster.HostConfig`.
    :param namespace: a prefix that should be added to all keys.
    :param serializer_cls: the serialization class you want to use.
                           By default, it is :class:`~rc.JSONSerializer`.
    :param default_expire: default expiration time that is used if no
                           expire specified on :meth:`set`.
    :param router_cls: use this to override the redis router class,
                       default to be :class:`~rc.RedisCRC32HashRouter`.
    :param router_options: a dictionary of parameters that is useful for
                           setting other parameters of router
    :param pool_cls: use this to override the redis connection pool class,
                     default to be :class:`~redis.ConnectionPool`
    :param pool_options: a dictionary of parameters that is useful for
                         setting other parameters of pool
    :param max_concurrency: defines how many parallel queries can happen
                            at the same time
    :param poller_timeout: for multi key operations we use a select loop as
                           the parallel query implementation, use this
                           to specify timeout for the underlying pollers
                           (select/poll/kqueue/epoll).
    :param bypass_values: a list of return values that would be ignored by the
                          cache decorator and won't be cached at all.

    .. versionadded:: 0.3
        The `bypass_values` parameter was added.
    """

    def __init__(self, hosts, namespace=None, serializer_cls=None,
                 default_expire=3 * 24 * 3600, router_cls=None,
                 router_options=None, pool_cls=None, pool_options=None,
                 max_concurrency=64, poller_timeout=1.0, bypass_values=[]):
        BaseCache.__init__(self, namespace, serializer_cls, default_expire,
                           bypass_values)
        self.hosts = hosts
        self.router_cls = router_cls
        self.router_options = router_options
        self.pool_cls = pool_cls
        self.pool_options = pool_options
        self.max_concurrency = max_concurrency
        self.poller_timeout = poller_timeout

    def get_client(self):
        redis_cluster = RedisCluster(self.hosts, router_cls=self.router_cls,
                                     router_options=self.router_options,
                                     pool_cls=self.pool_cls,
                                     pool_options=self.pool_options)
        return redis_cluster.get_client(self.max_concurrency,
                                        self.poller_timeout)

    def set_many(self, mapping, expire=None):
        if not mapping:
            return True
        if expire is None:
            expire = self.default_expire
        string_mapping = {}
        for key, value in mapping.iteritems():
            string = self.serializer.dumps(value)
            string_mapping[self.namespace + key] = string
        return self.client.msetex(string_mapping, expire)

    def delete_many(self, *keys):
        if not keys:
            return True
        if self.namespace:
            keys = [self.namespace + key for key in keys]
        return self.client.mdelete(*keys)


class BatchManager(object):
    """Context manager that helps us with batching."""

    def __init__(self, cache):
        self.cache = cache

    def __enter__(self):
        self.cache._running_mode = BATCH_MODE
        return self.cache

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            self.cache.batch(cancel=True)
        else:
            self.cache.batch()
