.. _api:

API
===

.. module:: rc

This page covers all interfaces of RC.


Cache Object
------------

.. autoclass:: Cache
   :members:
   :inherited-members:


Cache Cluster Object
--------------------

.. autoclass:: CacheCluster
   :members:
   :inherited-members:


Serializer
----------

.. autoclass:: BaseSerializer
   :members:
   :inherited-members:

.. autoclass:: JSONSerializer
   :members:
   :inherited-members:

.. autoclass:: PickleSerializer
   :members:
   :inherited-members:


Redis Router
------------

The base router class provides a simple way to replace the router cls that
cache cluster is using.

.. autoclass:: BaseRedisRouter
   :members:
   :inherited-members:

.. autoclass:: RedisCRC32HashRouter
   :members:
   :inherited-members:

.. autoclass:: RedisConsistentHashRouter
   :members:
   :inherited-members:


Testing Objects
---------------

.. autoclass:: NullCache
   :members:
   :inherited-members:
