# -*- coding: utf-8 -*-
from rc.cache import BaseCache


class NullCache(BaseCache):
    """Use this for unit test.  This doesn't cache."""

    def __init__(self, *args, **kwargs):
        BaseCache.__init__(self)

    def get(self, key):
        """Always return `None`"""
        return

    def set(self, key, value, time=None):
        """Always return `True`"""
        return True

    def delete(self, key):
        """Always return `True`"""
        return True

    def get_many(self, *keys):
        """Always return a list of `None`"""
        return [None for key in keys]


class FakeRedisCache(BaseCache):
    """Uses a fake redis server as backend.  It depends on the
    `fakeredis`_ library.

    .. _fakeredis: https://github.com/jamesls/fakeredis

    :param namespace: a prefix that should be added to all keys.
    :param serializer_cls: the serialization class you want to use.
                           By default, it is :class:`rc.JSONSerializer`.
    :param default_expire: default expiration time that is used if no
                           expire specified on :meth:`set`.
    """

    def __init__(self, namespace=None, serializer_cls=None,
                 default_expire=3 * 24 * 3600):
        BaseCache.__init__(self, namespace, serializer_cls, default_expire)

    def get_client(self):
        import fakeredis
        return fakeredis.FakeStrictRedis()
