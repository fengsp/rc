import pytest

from rc.promise import Promise


def test_promise_resolve():
    p = Promise()
    assert p.is_pending
    assert not p.is_resolved
    assert p.value is None
    p.resolve('value')
    assert not p.is_pending
    assert p.is_resolved
    assert p.value == 'value'
    with pytest.raises(RuntimeError):
        p.resolve('value again')


def test_promise_then():
    p = Promise()
    d = {}
    v = p.then(lambda v: d.setdefault('key', v))
    p.resolve('value')
    assert v.value == 'value'
    assert d['key'] == 'value'
