.. _api:

API
===

.. module:: rc

This page covers all interfaces of RC.


Base Cache System API
---------------------

.. currentmodule:: rc.cache

.. autoclass:: BaseCache
   :members:


Cluster Host Config
-------------------

.. currentmodule:: rc.redis_cluster

.. autoclass:: HostConfig
   :members:


Cache Object
------------

.. currentmodule:: rc

.. autoclass:: Cache
   :members:


Cache Cluster Object
--------------------

.. autoclass:: CacheCluster
   :members:


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
