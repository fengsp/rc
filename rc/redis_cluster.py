import weakref

from redis.connection import ConnectionPool, UnixDomainSocketConnection
try:
    from redis.connection import SSLConnection
except ImportError:
    SSLConnection = None

from rc.redis_clients import RedisClusterClient
from rc.redis_router import RedisCRC32HashRouter


class HostConfig(object):

    def __init__(self, host_name, host='localhost', port=6379,
                 unix_socket_path=None, db=0, password=None,
                 ssl=False, ssl_options=None):
        self.host_name = host_name
        self.host = host
        self.port = port
        self.unix_socket_path = unix_socket_path
        self.db = db
        self.password = password
        self.ssl = ssl
        self.ssl_options = ssl_options

    def __repr__(self):
        identity_dict = {
            'host': self.host,
            'port': self.port,
            'unix_socket_path': self.unix_socket_path,
            'db': self.db,
        }
        return '<%s %s>' % (
            self.__class__.__name__,
            ' '.join('%s=%s' % x for x in sorted(identity_dict.items())),
        )


class RedisCluster(object):
    """The redis cluster is the object that holds the connection pools to
    the redis nodes.

    `hosts` is a dictionary of hosts that maps the host host_name to
    configuration parameters.  The parameters are ...
    """

    def __init__(self, hosts, router_cls=None, pool_cls=None,
                 pool_options=None):
        if router_cls is None:
            router_cls = RedisCRC32HashRouter
        if pool_cls is None:
            pool_cls = ConnectionPool
        if pool_options is None:
            pool_options = {}
        self.router_cls = router_cls
        self.pool_cls = pool_cls
        self.pool_options = pool_options
        self.hosts = {}
        for host_name, host_config in hosts.iteritems():
            self.hosts[host_name] = HostConfig(**host_config)
        self.router = self.router_cls(self.hosts)
        #: connection pools of all hosts
        self._pools = {}

    def get_pool_of_host(self, host_name):
        """Returns the connection pool for a certain host."""
        pool = self._pools.get(host_name)
        if pool is not None:
            return pool
        else:
            host_config = self.hosts[host_name]
            pool_options = dict(self.pool_options)
            pool_options['db'] = host_config.db
            pool_options['password'] = host_config.password
            if host_config.unix_socket_path is not None:
                pool_options['path'] = host_config.unix_socket_path
                pool_options['connection_class'] = UnixDomainSocketConnection
            else:
                pool_options['host'] = host_config.host
                pool_options['port'] = host_config.port
                if host_config.ssl:
                    if SSLConnection is None:
                        raise RuntimeError('SSL connections are not supported')
                    pool_options['connection_class'] = SSLConnection
                    pool_options.update(host_config.ssl_options or {})
            pool = self.pool_cls(**pool_options)
            self._pools[host_name] = pool
            return pool

    def get_cluster_client(self):
        """Returns a cluster client.  This client can automatically route
        the requests to the corresponding node."""
        return RedisClusterClient(RedisClusterPool(self))


class RedisClusterPool(object):
    """The cluster pool works with the cluster client to get the correct pool.
    """

    def __init__(self, cluster):
        self.cluster = cluster

    def get_connection(self, command_name, host_name):
        real_pool = self.cluster.get_pool_of_host(host_name)
        connection = real_pool.get_connection(command_name)
        connection.__birth_pool = weakref.ref(real_pool)
        return connection

    def release(self, connection):
        real_pool = connection.__birth_pool()
        if real_pool is not None:
            real_pool.release(connection)
