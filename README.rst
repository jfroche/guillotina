Introduction
============

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
   :target: http://guillotina.readthedocs.io/en/latest/

.. image:: https://travis-ci.org/plone/guillotina.svg?branch=master
   :target: https://travis-ci.org/plone/guillotina

.. image:: https://coveralls.io/repos/github/plone/guillotina/badge.svg?branch=master
   :target: https://coveralls.io/github/plone/guillotina?branch=master
   :alt: Test Coverage

.. image:: https://img.shields.io/pypi/pyversions/guillotina.svg
   :target: https://pypi.python.org/pypi/guillotina/
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/v/guillotina.svg
   :target: https://pypi.python.org/pypi/guillotina

.. image:: https://img.shields.io/pypi/l/guillotina.svg
   :target: https://pypi.python.org/pypi/guillotina/
   :alt: License

Please `read the detailed docs <http://guillotina.readthedocs.io/en/latest/>`_


This is the working project of the next generation Guillotina server based on asyncio.


Dependencies
------------

* python >= 3.6
* postgresql >= 9.6


Getting started with development
--------------------------------

We use buildout of course::

    virtualenv .
    ./bin/pip install zc.buildout
    ./bin/buildout

The buildout installs the app itself, code analysis tools, and a test runner.

Run postgresql
--------------

If you don't have a postgresql server to play with, you can run one easily
with docker.

In the terminal::

  make run-postgres


Run the server
--------------

To run the server::

    ./bin/guillotina


Then...

    curl http://localhost:8080


Or, better yet, use postman to start playing with API.


Run tests
---------

We're using py.test::

    ./bin/py.test src

and for test coverage::

    ./bin/py.test --cov=guillotina guillotina/

With file watcher...

    ./bin/ptw guillotina --runner=./bin/py.test


To run tests with cockroach db:

   USE_COCKROACH=true ./bin/pytest guillotina

Default
-------

Default root access can be done with AUTHORIZATION header : Basic root:root


Docker
------

You can also run Guillotina with Docker!


First, run postgresql:

    docker run --rm \
        -e POSTGRES_DB=guillotina \
        -e POSTGRES_USER=guillotina \
        -p 127.0.0.1:5432:5432 \
        --name postgres \
        postgres:9.6

Then, run guillotina:

    docker run --rm -it \
        --link=postgres \
        -p 127.0.0.1:8080:8080 \
        -v $(echo $PWD):/g \
        guillotina/guillotina \
        --name g \
        g -c /g/config.yaml


This assumes you have a config.yaml in your current working directory


Roadmap for 2.0
---------------

- be able to configure renderer from function view configuration
- match on more predicates
- get rid of renderer, in favor of predicates for diff output
- view functions can take 2, 1 or zero args
- handle routes in definitions...
