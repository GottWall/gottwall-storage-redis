#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gw_storage_redis.config
~~~~~~~~~~~~~~~~~~~~~~~

Redist Storage GottWall config

:copyright: (c) 2014 by GottWall team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
:github: http://github.com/GottWall/gottwall-storage-redis
"""


STORAGE = 'gottwall.storages.MemoryStorage'

BACKENDS = {}

TEMPLATE_DEBUG = True

STORAGE_SETTINGS = dict(
    HOST = 'localhost',
    PORT = 6379,
    PASSWORD = None,
    DB = 2
)



USERS = ["alexandr.s.rus@gmail.com"]

SECRET_KEY = "dwefwefwefwecwef"

# http://pulic_key:secret_key@host.com

PROJECTS = {"test_project": "my_public_key",
            "another_project": "public_key2"}

cookie_secret="fkewrlhfwhrfweiurbweuybfrweoubfrowebfioubweoiufbwbeofbowebfbwup2XdTP1o/Vo="

TEMPLATE_DEBUG = True


DATABASE = {
    "ENGINE": "postgresql+psycopg2",
    "HOST": "localhost",
    "PORT": 5432,
    "USER": "postgres",
    "PASSWORD": "none",
    "NAME": "gottwall"
    }

PREFIX = ""
