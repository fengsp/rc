rc: the redis cache
===================

.. image:: _static/rc.png
   :alt: RC: the redis cache
   :class: floatingflask

Welcome to rc's documentation.  Caching can be fun and easy.  This is one
library that implements cache system for redis in Python.  It is for use
with web applications and Python scripts.  It comes with really handy apis
for easy drop-in use with common tasks, including caching decorators.  It
can be used to build a cache cluster which has a routing system that allows
you to automatically set cache on different servers, sharding can be really
easy now.  You can use it to batch fetch multiple cache results back, for
a cluster, it even does the job in parallel, we fetch results from all servers
concurrently, which means much higher performance.

It uses the `redis`_ server, which is a in-memory key-value data structure
server.  It does not implement any other backends like filesystem and does not
intend to do so.  Mostly we want to use a key-value server like redis, if you
have special needs, it is easy to write one cache decorator that stores
everything in memory using a dict or you can check out other libraries.


.. _redis: http://redis.io/


User's Guide
------------

This part of the documentation begins with installation, followed by more
instructions for doing cache with rc.

.. toctree::
   :maxdepth: 2

   foreword
   installation
   quickstart
   tutorial
   cache
   cache_config
   cache_cluster_config
   serializer
   redis_cluster_router
   testing
   patterns/index


API Reference
-------------

This part of the documentation contains information on a specific function,
class or method.

.. toctree::
   :maxdepth: 2

   api
