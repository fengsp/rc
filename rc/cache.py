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
    :param default_expiration: default expiration time that is used if no
                               expire specified on :meth:`set`.
    """

    def __init__(self, key_prefix=None, serializer_cls=None,
                 default_expiration=3 * 24 * 3600):
        if serializer_cls is None:
            serializer_cls = JSONSerializer
        self.key_prefix = key_prefix or ''
        self.serializer_cls = serializer_cls
        self.default_expiration = default_expiration

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

    def set(self, key, value, expire=None):
        """Adds or overwrites key/value to the cache.   The value expires in
        time seconds.

        :param key: cache key
        :param value: value for the key
        :param expire: expiration time
        :return: Whether the key has been set
        """
        if expire is None:
            expire = self.default_expiration
        string = self.serializer.dumps(value)
        return self.client.setex(self.key_prefix + key, expire, string)

    def delete(self, key):
        """Deletes the value for the cache key.

        :param key: cache key
        :return: Whether the key has been deleted
        """
        return self.client.delete(self.key_prefix + key)

    def get_many(self, *keys):
        """Returns the a list of values for the cache keys."""
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]
        return [self.serializer.loads(s) for s in self.client.mget(keys)]

    def set_many(self, mapping, expire=None):
        """Sets multiple keys and values using dictionary.
        The values expires in time seconds.

        :param mapping: a dictionary with key/values to set
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
    :param default_expiration: default expiration time that is used if no
                               expire specified on :meth:`set`.
    :param redis_options: a dictionary of parameters that are useful for
                          setting other parameters to the StrictRedis client.
    """

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, key_prefix=None, serializer_cls=None,
                 default_expiration=3 * 24 * 3600, redis_options=None):
        BaseCache.__init__(self, key_prefix, serializer_cls,
                           default_expiration)
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
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]
        return self.client.delete(*keys)


class CacheCluster(BaseCache):
    """The core object behind rc."""

    def __init__(self):
        pass
