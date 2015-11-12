.. _installation:

Installation
============

Want to give rc a try quickly?  Let's start by installing it, you need Python
2.6 or newer.


virtualenv
----------

Virtualenv might be something you want to use for development!  If you do not
have it yet, try the following command::

    $ sudo pip install virtualenv

Since we have virtualenv installed now, let's create one working environment::

    $ mkdir myproject
    $ cd myproject
    $ virtualenv venv
    $ . venv/bin/activate

It is time to get rc::

    $ pip install rc

Done!


System Wide
-----------

Install it for all users on the system::

    $ sudo pip install rc


Development Version
-------------------

Try the latest version::

    $ . venv/bin/activate
    $ git clone http://github.com/fengsp/rc.git
    $ cd rc
    $ python setup.py develop
