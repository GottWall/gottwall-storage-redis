#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
gottwall_storage_redis
~~~~~~~~~~~~~~~~~~~~~~

Redis storage for GottWall statistics aggregator

:copyright: (c) 2012 - 2014 by GottWall team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""


import sys

import os
import os.path as op
from setuptools import setup
from setuptools.command.test import test as BaseTestCommand

try:
    readme_content = open(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), "README.rst")).read()
except Exception as e:
    print(e)
    readme_content = __doc__

VERSION = "0.0.1"


def run_tests():
    from tests import suite
    return suite()

py_ver = sys.version_info

#: Python 2.x?
is_py2 = (py_ver[0] == 2)

#: Python 3.x?
is_py3 = (py_ver[0] == 3)


try:
    dev_require = open(op.join(op.abspath(
        op.dirname(__file__)), "dev_req.txt")).readlines()
except Exception as e:
    print(e)
    dev_require = []

tests_require = [
    'nose',
    'unittest2',
    'redis==2.9.0',
    'tornado-redis==2.4.15',
    'mock>=0.8.0']


install_requires = [
    "redis==2.9.0",
    "tornado-redis==2.4.15",
    "gottwall==0.5.0"]


class TestCommand(BaseTestCommand):
    def finalize_options(self):
        BaseTestCommand.finalize_options(self)
        self.test_args = ['__main__.run_tests']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name="gottwall-storage-redis",
    version=VERSION,
    description="Redis storage for GottWall statistics aggregator",
    long_description=readme_content,
    author="Alex Lispython",
    author_email="alex@obout.ru",
    maintainer="Alexandr Lispython",
    maintainer_email="alex@obout.ru",
    url="https://github.com/GottWall/gottwall-storage-redis",
    packages=["gw_storage_redis"],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'tests': tests_require,
        'dev': dev_require
    },
    license="BSD",
    platforms = ['Linux', 'Mac'],
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries"
        ],
    test_suite = '__main__.run_tests',
    #cmdclass={'test': TestCommand}
    )
