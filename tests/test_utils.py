from rc.utils import generate_key_for_cached_func


def test_generate_key():
    def func():
        pass
    cache_key = generate_key_for_cached_func(None, func, 'foo')
    assert cache_key == u'test_utils func foo'
    cache_key = generate_key_for_cached_func('prefix', func, 'foo')
    assert cache_key == u'prefix test_utils func foo'
    cache_key = generate_key_for_cached_func(None, func, 'foo', k='v')
    assert cache_key == u'test_utils func foo k=v'
    cache_key = generate_key_for_cached_func(None, func,
                                             'foo', k='v', k2='v2')
    assert cache_key == u'test_utils func foo k=v k2=v2'

    def method(self):
        pass
    cache_key = generate_key_for_cached_func(None, method, 'foo')
    assert cache_key == u'test_utils method foo'
    cache_key = generate_key_for_cached_func(None, method, None, 'foo')
    assert cache_key == u'test_utils method None foo'

    def method(cls):
        pass
    cache_key = generate_key_for_cached_func(None, method, 'foo')
    assert cache_key == u'test_utils method foo'
