import time
from itertools import izip

from redis import StrictRedis
from rc.redis_cluster import RedisCluster


cluster = RedisCluster({
    0: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 0},
    1: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 1},
    2: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 2},
    3: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 3},
    4: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 4},
    5: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 5},
    6: {'host': 'redis01.aws.dev', 'port': 4001, 'db': 6},
})
cluster_router = cluster.router
cluster_client = cluster.get_client()
clients = [
    StrictRedis(host='redis01.aws.dev', port=4001, db=0),
    StrictRedis(host='redis01.aws.dev', port=4001, db=1),
    StrictRedis(host='redis01.aws.dev', port=4001, db=2),
    StrictRedis(host='redis01.aws.dev', port=4001, db=3),
    StrictRedis(host='redis01.aws.dev', port=4001, db=4),
    StrictRedis(host='redis01.aws.dev', port=4001, db=5),
    StrictRedis(host='redis01.aws.dev', port=4001, db=6),
]


def bench_cluster(keys):
    print 'Benching cluster...'
    start = time.time()
    while keys:
        cluster_client.mget(keys[:1000])
        keys = keys[1000:]
    print time.time() - start


def bench_clients(keys):
    print 'Benching clients...'
    start = time.time()
    while keys:
        current_keys = keys[:1000]
        hostname_to_keys = {}
        for key in current_keys:
            hostname = cluster_router.get_host_for_key(key)
            hostname_to_keys.setdefault(hostname, []).append(key)
        result = {}
        for hostname, hostkeys in hostname_to_keys.iteritems():
            rv = clients[hostname].mget(hostkeys)
            result.update(dict(izip(hostkeys, rv)))
        [result[k] for k in current_keys]
        keys = keys[1000:]
    print time.time() - start


if __name__ == '__main__':
    keys = range(100000)
    bench_cluster(keys)
    bench_clients(keys)
"""Benching cluster...
2.86095499992
Benching clients...
10.8946011066
"""
