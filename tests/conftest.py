import tempfile
import uuid
import os
import time
import socket
import shutil
from subprocess import Popen, PIPE

import pytest


devnull = open(os.devnull, 'w')


class RedisServer(object):

    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.redis = Popen(['redis-server', '-'], stdin=PIPE, stdout=devnull)
        self.redis.stdin.write('''
        port 0
        unixsocket %s
        save ""''' % socket_path)
        self.redis.stdin.flush()
        self.redis.stdin.close()
        while 1:
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(socket_path)
            except IOError:
                time.sleep(0.05)
                continue
            else:
                break

    def shutdown(self):
        self.redis.kill()
        self.redis.wait()
        os.remove(self.socket_path)

    def __del__(self):
        try:
            self.shutdown()
        except:
            pass


@pytest.fixture(scope='session')
def redis_hosts(request):
    socket_dir = tempfile.mkdtemp()
    hosts = {}
    servers = []
    for i in range(4):
        socket_path = os.path.join(socket_dir, str(uuid.uuid4()))
        server = RedisServer(socket_path)
        for j in range(4):
            hosts['cache-server-%s' % (i * 4 + j)] = {
                'unix_socket_path': socket_path,
                'db': j,
            }
        servers.append(server)

    def fin():
        for server in servers:
            server.shutdown()
        shutil.rmtree(socket_dir)
    request.addfinalizer(fin)
    return hosts


@pytest.fixture(scope='session')
def redis_unix_socket_path(redis_hosts):
    return redis_hosts.values()[0]['unix_socket_path']
