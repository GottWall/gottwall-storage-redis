Welcome to gottwall-backend-redis's documentation!
==================================================

gottwall-storage-redis is a Redis storage  for `GottWall metrics aggregation platform <http://github.com/GottWall/GottWall>`_

.. image:: https://secure.travis-ci.org/GottWall/gottwall-storage-redis.png
	   :target: https://secure.travis-ci.org/GottWall/gottwall-storage-redis

INSTALLATION
------------

To use gottwall-storage-redis  use `pip` or `easy_install`:

``pip install gottwall-storage-redis``

or

``easy_install gottwall-storage-redis``


USAGE
-----

To configure GottWall with `gottwall-storage-redis` you need specify backend in GottWall config.

.. sourcecode:: python

   STORAGE = "gw_storage_redis.RedisStorage"

   STORAGE_SETTINGS = {
       "HOST": "localhost",
	   "PORT": 6379,
	   "PASSWORD": "",
	   "DB": 2
   }



CONTRIBUTE
----------

We need you help.

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
   There is a Contributor Friendly tag for issues that should be ideal for people who are not very familiar with the codebase yet.
#. Fork `the repository`_ on Github to start making your changes to the **develop** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.

.. _`the repository`: https://github.com/GottWall/gottwall-storage-redis/
