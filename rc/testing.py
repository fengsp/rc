# -*- coding: utf-8 -*-
from rc.cache import BaseCache


class NullCache(BaseCache):
    """Use this for unit test."""

    def __init__(self, *args, **kwargs):
        BaseCache.__init__(self)

    def get(self, key):
        return

    def set(self, key, value, time=None):
        pass

    def delete(self, key):
        pass

    def get_many(self, *keys):
        return [None for key in keys]
