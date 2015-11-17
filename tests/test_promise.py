import pytest

from rc.promise import Promise


def test_promise_resolve():
    p = Promise()
    assert p.is_pending
    assert not p.is_resolved
    assert p.result is None
    p.resolve('value')
    assert not p.is_pending
    assert p.is_resolved
    assert p.result == 'value'
    with pytest.raises(RuntimeError):
        p.resolve('value again')


def test_promise_on_resolve():
    p = Promise()
    d = {}
    v = p.on_resolve(lambda v: d.setdefault('key', v))
    p.resolve('value')
    assert v.result == 'value'
    assert d['key'] == 'value'
