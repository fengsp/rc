# -*- coding: utf-8 -*-
from rc.redis_clients import RedisClient
from rc.redis_cluster import RedisCluster
from rc.serializer import JSONSerializer


class cached_property(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype):
        rv = obj.__dict__[self.fget.__name__] = self.fget(obj)
        return rv


class BaseCache(object):
    """Baseclass for all redis cache systems.

    :param key_prefix: a prefix that should be added to all keys
    :param serializer_cls: the serialization class you want to use.
    :param default_expires_time: default expiration time that is used if no
                                 time specified on :meth:`set`.
    """

    def __init__(self, key_prefix=None, serializer_cls=None,
                 default_expires_time=3 * 24 * 3600):
        if serializer_cls is None:
            serializer_cls = JSONSerializer
        self.key_prefix = key_prefix or ''
        self.serializer_cls = serializer_cls
        self.default_expires_time = default_expires_time

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
        return self.serializer.loads(self.client.get(self.key_prefix + key))

    def set(self, key, value, time=None):
        """Adds or overwrites key/value to the cache.   The value expires in
        time seconds.

        :param key: cache key
        :param value: value for the key
        """
        if time is None:
            time = self.default_expires_time
        string = self.serializer.dumps(value)
        self.client.setex(self.key_prefix + key, time, string)

    def delete(self, key):
        """Deletes the value for the cache key.

        :param key: cache key
        """
        self.client.delete(self.key_prefix + key)

    def get_many(self, *keys):
        """Returns the a list of values for the cache keys."""
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]
        return [self.serializer.loads(s) for s in self.client.mget(keys)]

    def set_many(self, mapping, time=None):
        """Sets multiple keys and values using dictionary.
        The values expires in time seconds.

        :param mapping: a dictionary with key/values to set
        """
        for key, value in mapping.iteritems():
            self.set(key, value, time)

    def delete_many(self, *keys):
        """Deletes multiple keys."""
        for key in keys:
            self.delete(key)


class NullCache(BaseCache):
    """Use this for unit test."""

    def __init__(self, *args, **kwargs):
        BaseCache.__init__(self)

    def get(self, key):
        return

    def set(self, key, value, time=None):
        pass

    def delete(self, key):
        pass

    def get_many(self, *keys):
        return [None for key in keys]


class Cache(BaseCache):
    """Uses a single Redis server as backend.

    :param host: address of the Redis, this is compatible with the official
                 Python StrictRedis cilent (redis-py).
    :param port: port number of the Redis server.
    :param db: db numeric index of the Redis server.
    :param password: password authentication for the Redis server.
    :param socket_timeout: socket timeout for the StrictRedis client.
    :param key_prefix: a prefix that should be added to all keys.
    :param serializer_cls: the serialization class you want to use.
    :param default_expires_time: default expiration time that is used if no
                                 time specified on :meth:`set`.
    :param redis_options: a dictionary of parameters that are useful for
                          setting other parameters to the StrictRedis client.
    """

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, key_prefix=None, serializer_cls=None,
                 default_expires_time=3 * 24 * 3600, redis_options=None):
        BaseCache.__init__(self, key_prefix, serializer_cls,
                           default_expires_time)
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
        """Deletes multiple keys."""
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]
        self.client.delete(*keys)


class CacheCluster(BaseCache):
    """The core object behind rc."""

    def __init__(self):
        pass
