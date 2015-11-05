import pytest

from rc.poll import supported_pollers
from rc import redis_clients
from rc.redis_cluster import RedisCluster


@pytest.mark.parametrize('poller', supported_pollers)
def test_all_pollers(redis_hosts, poller, monkeypatch):
    monkeypatch.setattr(redis_clients, 'poller', poller)

    # assert len(supported_pollers) == 4
    redis_cluster = RedisCluster(redis_hosts)
    cluster_client = redis_cluster.get_client()
    keys = []
    for i in range(10):
        key = 'key-%s' % i
        keys.append(key)
        cluster_client.set(key, i)
    assert cluster_client.mget(keys) == map(str, range(10))
