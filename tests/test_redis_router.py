import pytest

from rc.redis_cluster import RedisCluster


def test_redis_router_basics():
    cluster = RedisCluster({
        0: {},
        1: {},
        2: {},
    })
    router = cluster.router

    assert router.get_key_for_command('GET', 'c') == 'c'
    assert router.get_key_for_command('SET', 'g') == 'g'
    with pytest.raises(RuntimeError):
        router.get_key_for_command('MGET', ['a', 'b', 'c'])

    assert router.get_host_for_key('c') == 0
    assert router.get_host_for_key('g') == 1
    assert router.get_host_for_key('a') == 2

    assert router.get_host_for_command('GET', 'c') == 0
    assert router.get_host_for_command('GET', 'g') == 1
    assert router.get_host_for_command('SET', 'a') == 2
