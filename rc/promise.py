PENDING_STATE = 0
RESOLVED_STATE = 1


class Promise(object):
    """A promise object.  You can access ``promise.result`` to get the
    resolved value.  Here is one example::

        p = Promise()
        assert p.is_pending
        assert not p.is_resolved
        assert p.result is None
        p.resolve('value')
        assert not p.is_pending
        assert p.is_resolved
        assert p.result == 'value'
    """

    def __init__(self):
        #: the value for this promise if it's resolved
        self.result = None
        self._state = PENDING_STATE
        self._callbacks = []

    def resolve(self, value):
        """Resolves with value."""
        if self._state != PENDING_STATE:
            raise RuntimeError('Promise is no longer pending.')
        self.result = value
        self._state = RESOLVED_STATE
        for callback in self._callbacks:
            callback(value)

    @property
    def is_resolved(self):
        """Return `True` if the promise is resolved."""
        return self._state == RESOLVED_STATE

    @property
    def is_pending(self):
        """Return `True` if the promise is pending."""
        return self._state == PENDING_STATE

    def then(self, on_resolve=None):
        """Add one callback that is called with the resolved value when the
        promise is resolved, and return the promise itself.  One demo::

            p = Promise()
            d = {}
            p.then(lambda v: d.setdefault('key', v))
            p.resolve('value')
            assert p.result == 'value'
            assert d['key'] == 'value'
        """
        if on_resolve is not None:
            if self._state == PENDING_STATE:
                self._callbacks.append(on_resolve)
            elif self._state == RESOLVED_STATE:
                on_resolve(self.result)
        return self

    def __repr__(self):
        if self._state == PENDING_STATE:
            v = '(pending)'
        else:
            v = repr(self.result)
        return '<%s %s>' % (
            self.__class__.__name__,
            v,
        )
