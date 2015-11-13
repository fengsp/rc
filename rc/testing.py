# -*- coding: utf-8 -*-
from rc.cache import BaseCache


class NullCache(BaseCache):
    """Use this for unit test.  This doesn't cache."""

    def __init__(self, *args, **kwargs):
        BaseCache.__init__(self)

    def get(self, key):
        """Always return `None`"""
        return

    def set(self, key, value, time=None):
        """Always return `True`"""
        return True

    def delete(self, key):
        """Always return `True`"""
        return True

    def get_many(self, *keys):
        """Always return a list of `None`"""
        return [None for key in keys]
