from rc.serializer import PickleSerializer, JSONSerializer


def test_pickle_serializer():
    serializer = PickleSerializer()
    obj = 1
    string = serializer.dumps(obj)
    assert obj == serializer.loads(string)
    obj = 'test'
    string = serializer.dumps(obj)
    assert obj == serializer.loads(string)
    obj = {'key': 'value'}
    string = serializer.dumps(obj)
    assert obj == serializer.loads(string)
    assert serializer.loads(None) is None


def test_json_serializer():
    serializer = JSONSerializer()
    obj = 1
    string = serializer.dumps(obj)
    assert obj == serializer.loads(string)
    obj = 'test'
    string = serializer.dumps(obj)
    assert obj == serializer.loads(string)
    obj = {'key': 'value'}
    string = serializer.dumps(obj)
    assert obj == serializer.loads(string)
    assert serializer.loads(None) is None
