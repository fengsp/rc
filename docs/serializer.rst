.. _serializer:

Serializer
==========

This page we talk about serializers.


JSON Serializer
---------------

It is simple and fast.  The downside is that it cannot serialize enough types
of Python objects.  For more details check out :class:`~rc.JSONSerializer`.


Pickle Serializer
-----------------

More Python types are supported.  The downside is that it might be slower than
JSON, unpickling can run arbitrary code, and using `pickle` to transfer data
between programs in different languages is almost impossible, check out
:class:`~rc.PickleSerializer`.


Build Your Own Serializer
-------------------------

Subclass :class:`~rc.BaseSerializer`, implement
:meth:`~rc.BaseSerializer.dumps` and :meth:`~rc.BaseSerializer.loads`.

Here is one simple example::

    import json

    from rc.serializer import BaseSerializer

    class IterEncoder(json.JSONEncoder):

        def default(self, o):
            try:
               iterable = iter(o)
            except TypeError:
               pass
            else:
               return list(iterable)
            return json.JSONEncoder.default(self, o)

    class MyJSONSerializer(BaseSerializer):
        """One serializer that uses JSON and support arbitrary iterators"""

        def dumps(self, obj):
            return json.dumps(obj, cls=IterEncoder)

        def loads(self, string):
            if string is None:
                return
            return json.loads(string)
