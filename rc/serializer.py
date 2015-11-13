# -*- coding: utf-8 -*-
import json
try:
    import cPickle as pickle
except ImportError:
    import pickle


class BaseSerializer(object):
    """Baseclass for serializer.  Subclass this to get your own serializer."""

    def dumps(self, obj):
        """Dumps an object into a string for redis."""
        raise NotImplementedError()

    def loads(self, string):
        """Read a serialized object from a string."""
        raise NotImplementedError()


class PickleSerializer(BaseSerializer):
    """One serializer that uses Pickle"""

    def dumps(self, obj):
        return pickle.dumps(obj)

    def loads(self, string):
        if string is None:
            return
        return pickle.loads(string)


class JSONSerializer(BaseSerializer):
    """One serializer that uses JSON"""

    def dumps(self, obj):
        return json.dumps(obj)

    def loads(self, string):
        if string is None:
            return
        return json.loads(string)
