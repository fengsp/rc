from rc.redis_cluster import RedisCluster


def test_redis_cluster_client_basic_operations(redis_hosts):
    cluster = RedisCluster(redis_hosts)
    client = cluster.get_client()

    keys = []
    for i in xrange(10):
        key = 'test key: %s' % i
        keys.append(key)
        client.set(key, i)
    for i, key in enumerate(keys):
        assert client.get(key) == str(i)
    assert client.mget(keys) == map(str, range(10))
