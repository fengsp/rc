# -*- coding: utf-8 -*-
"""
    rc
    ~~

    The redis cache.

    :copyright: (c) 2016 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""
from rc.cache import Cache, CacheCluster
from rc.serializer import BaseSerializer, JSONSerializer, PickleSerializer
from rc.redis_router import BaseRedisRouter, RedisCRC32HashRouter
from rc.redis_router import RedisConsistentHashRouter
from rc.testing import NullCache, FakeRedisCache


__version__ = '0.3.1'


__all__ = [
    'Cache', 'CacheCluster',

    'BaseSerializer', 'JSONSerializer', 'PickleSerializer',

    'BaseRedisRouter', 'RedisCRC32HashRouter', 'RedisConsistentHashRouter',

    'NullCache', 'FakeRedisCache',
]
