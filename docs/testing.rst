.. _testing:

Testing
=======

Testing applications that use RC.


Null Cache
----------

Simple idea, just create one :class:`~rc.NullCache` object that does not
cache at all when you are doing unit test.


Fake Redis
----------

Use a fake redis as backend, this is existing for testing purposes only.
It depends on the `fakeredis`_ library, install it first::

    $ pip install fakeredis

.. _fakeredis: https://github.com/jamesls/fakeredis

For more details, check out :class:`~rc.FakeRedisCache`.
