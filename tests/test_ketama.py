from rc.ketama import HashRing


def test_basic():
    nodes = ['node01', 'node02', 'node03', 'node04']
    hashring = HashRing(nodes)
    keys = [u'key-%s' % i for i in range(500)]
    keys_nodes = [hashring.get_node(k) for k in keys]
    for node in nodes:
        assert node in keys_nodes

    keys = ['key-%s' % i for i in range(500, 1000)]
    keys_nodes = [hashring.get_node(k) for k in keys]
    for node in nodes:
        assert node in keys_nodes
