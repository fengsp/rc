from rc.redis_cluster import RedisCluster, HostConfig


def test_cluster_constructor():
    cluster = RedisCluster({
        0: {'password': 'pass', 'ssl': True},
        1: {'host': '127.0.0.1', 'port': 10000, 'db': 1},
        2: {'unix_socket_path': '/tmp/redis_socket'},
    })

    assert cluster.hosts[0].host_name == 0
    assert cluster.hosts[0].host == 'localhost'
    assert cluster.hosts[0].port == 6379
    assert cluster.hosts[0].unix_socket_path is None
    assert cluster.hosts[0].db == 0
    assert cluster.hosts[0].password == 'pass'
    assert cluster.hosts[0].ssl is True
    assert cluster.hosts[0].ssl_options is None

    assert cluster.hosts[1].host_name == 1
    assert cluster.hosts[1].host == '127.0.0.1'
    assert cluster.hosts[1].port == 10000
    assert cluster.hosts[1].unix_socket_path is None
    assert cluster.hosts[1].db == 1
    assert cluster.hosts[1].password is None
    assert cluster.hosts[1].ssl is False
    assert cluster.hosts[1].ssl_options is None

    assert cluster.hosts[2].host_name == 2
    assert cluster.hosts[2].host == 'localhost'
    assert cluster.hosts[2].port == 6379
    assert cluster.hosts[2].unix_socket_path == '/tmp/redis_socket'
    assert cluster.hosts[2].db == 0
    assert cluster.hosts[2].password is None
    assert cluster.hosts[2].ssl is False
    assert cluster.hosts[2].ssl_options is None


def test_host_config():
    host_config_01 = HostConfig('01')
    host_config_02 = HostConfig('02', password='pass', ssl=False)
    assert repr(host_config_01) == repr(host_config_02)


def test_cluster_pools():
    cluster = RedisCluster({
        0: {'password': 'pass', 'ssl': True},
        1: {'unix_socket_path': '/tmp/redis_socket'},
    })
    pool_for_0 = cluster.get_pool_of_host(0)
    pool_for_1 = cluster.get_pool_of_host(1)
    pool_for_0_again = cluster.get_pool_of_host(0)
    assert pool_for_0 is pool_for_0_again
    assert pool_for_0 is not pool_for_1
