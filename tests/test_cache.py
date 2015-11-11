# -*- coding: utf-8 -*-
import pytest

from rc.cache import NullCache, Cache


def test_null_cache():
    cache = NullCache()
    with pytest.raises(NotImplementedError):
        cache.client
    assert cache.get('key') is None
    cache.set('key', 'value')
    cache.delete('key')
    assert cache.get_many('key1', 'key2') == [None, None]
    cache.set_many({'key1': 'value1', 'key2': 'value2'})
    cache.delete_many('key1', 'key2')


def test_cache_basic_apis(redis_unix_socket_path):
    cache = Cache(redis_options={'unix_socket_path': redis_unix_socket_path})
    assert cache.get('key') is None
    cache.set('key', 'value')
    assert cache.get('key') == 'value'
    cache.delete('key')
    assert cache.get('key') is None

    assert cache.get_many('key1', 'key2') == [None, None]
    cache.set_many({'key1': 'value1', 'key2': 'value2'})
    assert cache.get_many('key1', 'key2') == ['value1', 'value2']
    cache.delete_many('key1', 'key2')
    assert cache.get_many('key1', 'key2') == [None, None]

    assert cache.get('key') is None
    cache.set('key', ['value'])
    assert cache.get('key') == ['value']
    cache.delete('key')
    assert cache.get('key') is None

    # import time
    # assert cache.get('key') is None
    # cache.set('key', 'value', 1)
    # time.sleep(1)
    # assert cache.get('key') is None


def test_cache_key_prefix(redis_unix_socket_path):
    cache01 = Cache(redis_options={'unix_socket_path': redis_unix_socket_path})
    cache02 = Cache(
        key_prefix='test:',
        redis_options={'unix_socket_path': redis_unix_socket_path})
    cache01.set('key', 'value')
    assert cache01.get('key') == 'value'
    assert cache02.get('key') is None
