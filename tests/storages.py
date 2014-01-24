#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
gw_storage_redis.tests
~~~~~~~~~~~~~~~~~~~~~~

Unittests for redis storage for GottWall

:copyright: (c) 2012 - 2014 by GottWall team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
:github: http://github.com/GottWall/gottwall-storage-redis
"""
import os
import datetime
from uuid import UUID

import tornado.gen
import tornado.ioloop

from gottwall.app import HTTPApplication
from gottwall.config import Config
import gottwall.default_config
from gottwall.utils.tests import async_test
import tornadoredis
from tornado.gen import Task

from gottwall.utils.tests import BaseTestCase, AsyncBaseTestCase

from gottwall.storages import MemoryStorage, BaseStorage
from gw_storage_redis.storage import RedisStorage
from gottwall.utils import MagicDict


HOST = os.environ.get('GOTTWALL_REDIS_HOST', "10.8.9.9")


class UtilsMixin(object):

    def get_embedded_metrics(self):

        return [{"metric_name": "test_metric_name1"},
                {"metric_name": "test_metric_name2",
                 "filter_name": "test_filter_name2",
                 "filter_value": "test_fitler_value2"}]

    @tornado.gen.engine
    def metric_meta_tests(self, storage):
        filters = {"filter1": "value",
                   "filter2": ["value1", "value2", "value2"]}

        res = yield Task(storage.save_metric_meta, "memory_storage", "metric_name",
                         filters=filters)

        self.assertTrue(res)

        self.assertEquals(storage._metrics["memory_storage"]["metric_name"]["filter1"], ["value"])
        self.assertEquals(storage._metrics["memory_storage"]["metric_name"]["filter2"],
                          ["value1", "value2"])

        metrics_res = (yield Task(storage.metrics, "memory_storage"))

        self.assertEquals(metrics_res,
                          {"metric_name": {"filter1": [filters['filter1']],
                                           "filter2": ["value1", "value2"]}})

    @tornado.gen.engine
    def methods_tests(self, storage):

        res = (yield Task(storage.make_embedded, project="test_project1", period="month",
                         metrics=self.get_embedded_metrics()))

        self.assertTrue(isinstance(res, UUID))

        embedded_res = (yield Task(storage.get_embedded, res))
        self.assertEquals(embedded_res['project'], "test_project1")
        self.assertEquals(embedded_res['period'], "month")
        self.assertEquals(len(embedded_res['metrics']), len(self.get_embedded_metrics()))


    @tornado.gen.engine
    def storage_tests(self, storage):

        project_name = self.random_str(10)
        metric_name = self.random_str(10)
        now = datetime.datetime.now()
        from_date = now - relativedelta(years=1)
        to_date = now + relativedelta(years=1)
        filters = {"filter1": True,
                   "filter2": ["web", "iphone", "android"]}

        data = self.build_data(from_date, to_date,
                               project_name, metric_name,
                               filters=filters)

        for item in data:
            storage.incr(project=project_name, name=metric_name,
                         timestamp=item['timestamp'],
                         filters={item['filter_name']: item['filter_value']},
                         value=item['value'])

        metrics_list = (yield Task(storage.get_metrics_list, project_name))

        self.assertTrue(metric_name in metrics_list)
        self.assertEquals(len(metrics_list), 1)

        filters_list = (yield Task(storage.get_filters, project_name, metric_name))

        self.assertTrue("filter1" in filters_list)
        self.assertTrue("filter2" in filters_list)
        self.assertEquals(len(filters), len(filters_list))

        self.assertTrue(1, len((yield Task(storage.get_filter_values,
                                           project_name, metric_name, "filter1"))))

        self.assertTrue(3, len((yield Task(storage.get_filter_values,
                                           project_name, metric_name, "filter2"))))

        metrics = yield Task(storage.metrics, project_name)
        self.assertEquals(metrics[metric_name]['filter1'], [True])
        self.assertEquals(sorted(metrics[metric_name]['filter2']), sorted(['android', 'iphone', 'web']))

        self.methods_tests(storage)

        # Test storage.query
        for period in ["year", "month", "day", "week", "hour", "minute"]:
            for filter_name, filter_value in (("filter1", True),
                                              ("filter2", "web"),
                                              ("filter2", "iphone"),
                                              (None, None)):

                d = (yield Task(storage.query, project_name,
                                metric_name, period,
                                from_date=from_date,
                                to_date=to_date,
                                filter_name=filter_name,
                                filter_value=filter_value))

                test_etalon_range = list(self.get_range(data, from_date, to_date,
                                                        period, filter_name, filter_value))

                for k1, k2 in zip(d['range'], test_etalon_range):
                    self.assertEquals(k1, k2)

                self.assertEquals(self.get_max(test_etalon_range), d['max'])
                self.assertEquals(self.get_min(test_etalon_range), d['min'])
                self.assertEquals(self.get_avg(test_etalon_range), d['avg'])

        # Test queryset
        for period in ["year", "month", "day", "week", "hour", "minute"]:
            for filter_name, filter_values in (("filter1", [True]),
                                               ("filter2", ['android', 'iphone', 'web'])):
                d = (yield Task(storage.query_set, project_name,
                                metric_name, period,
                                from_date=from_date,
                                to_date=to_date,
                                filter_name=filter_name))

                for value in filter_values:
                    test_etalon_range = list(self.get_range(data, from_date, to_date,
                                                            period, filter_name, value))
                    for k1, k2 in zip(d[value]['range'], test_etalon_range):
                        self.assertEquals(k1[0], k2[0])
                        self.assertEquals(k1[1], k2[1])

                    self.assertEquals(self.get_max(test_etalon_range), d[value]['max'])
                    self.assertEquals(self.get_min(test_etalon_range), d[value]['min'])
                    self.assertEquals(self.get_avg(test_etalon_range), d[value]['avg'])


class TestRedisClient(tornadoredis.Client):

    def __init__(self, *args, **kwargs):

        self._on_destroy = kwargs.get('on_destroy', None)
        if 'on_destroy' in kwargs:
            del kwargs['on_destroy']
        super(TestRedisClient, self).__init__(*args, **kwargs)

    def __del__(self):
        super(TestRedisClient, self).__del__()
        if self._on_destroy:
            self._on_destroy()


class RedisTestCaseMixin(object):

    @property
    def redis_settings(self):
        env = os.environ

        return {"HOST": env.get('GOTTWALL_REDIS_HOST', "10.8.9.8"),
                "PORT": env.get('GOTTWALL_REDIS_PORT', 6379),
                "DB": env.get('GOTTWALL_REDIS_DB', 0)}


    def setUp(self):
        super(RedisTestCaseMixin, self).setUp()
        self.client = self._new_client()
        self.client.flushdb()

    def tearDown(self):
        try:
            self.client.connection.disconnect()
            del self.client
        except AttributeError:
            pass
        super(RedisTestCaseMixin, self).tearDown()


    def _new_client(self, pool=None, on_destroy=None):
        client = TestRedisClient(io_loop=self.io_loop,
                                 host=self.redis_settings['HOST'],
                                 port=self.redis_settings['PORT'],
                                 selected_db=self.redis_settings['DB'],
                                 connection_pool=pool,
                                 on_destroy=on_destroy)

        return client


from dateutil.relativedelta import relativedelta



class RedisStorageTestCase(AsyncBaseTestCase, RedisTestCaseMixin, UtilsMixin):

    def setUp(self):
        super(RedisStorageTestCase, self).setUp()
        self.client = self._new_client()
        self.client.flushdb()

    def tearDown(self):
        try:
            self.client.flushdb()
            self.client.connection.disconnect()
            del self.client
        except AttributeError:
            pass
        super(RedisStorageTestCase, self).tearDown()

    def get_app(self):
        config = Config()
        config.from_object(gottwall.default_config)

        config.update({"STORAGE_SETTINGS": {
            "HOST": self.redis_settings['HOST']
            }})

        self.app = HTTPApplication(config)
        self.app.configure_app(self.io_loop)

        return self.app

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    @async_test
    @tornado.gen.engine
    def test_storage_utils(self):
        storage = RedisStorage(self.get_app())

        self.assertEquals(storage.make_key("redis_project_name", "metric_name", "week",
                                           filters={"status": "new",
                                                    "type": "registered"}),
                          "redis_project_name;metric_name;week;status|new/type|registered")

        self.assertTrue(isinstance(storage, RedisStorage))

        filters = {"filter1": "value",
                   "filter2": ["value1", "value2", "value2"]}

        client = self.client

        pipe = client.pipeline()
        storage.save_metric_meta(pipe, "redis_storage_test", "metric_name",
                                 filters=filters)

        (yield Task(pipe.execute))

        metrics = yield Task(
            client.smembers,
            storage.get_metrics_key("redis_storage_test"))

        self.assertEquals(len(metrics), 1)
        self.assertTrue("metric_name" in metrics)

        stored_filters = yield Task(
            client.smembers,
            storage.get_filters_names_key("redis_storage_test", "metric_name"))

        self.assertEquals(len(stored_filters), 2)

        for f, values in filters.items():

            stored_value = yield Task(
                client.smembers,
                storage.get_filters_values_key("redis_storage_test", "metric_name", f))

            self.assertEquals(set(values)
                              if isinstance(values, (list, tuple))
                              else set([values]),
                              stored_value)

        metrics = yield Task(storage.metrics, "redis_storage_test")

        self.assertEquals(metrics,
        {"metric_name": {"filter1": [filters['filter1']],
                         "filter2": ["value1", "value2"]}})

        self.stop()


    @async_test
    @tornado.gen.engine
    def test_metric_meta(self):
        """Get metrics structure
        """
        client = tornadoredis.Client(host=self.redis_settings['HOST'])
        app = self.get_app()
        app.configure_storage("gw_storage_redis.storage.RedisStorage")
        storage = app.storage

        pipe = client.pipeline()

        (yield Task(storage.save_metric_meta, pipe, "test_metric_meta_project", "metric_name",
                   filters={"hello": "world",
                            "test": ["value1", "value2"]}))

        self.stop()

    @async_test
    @tornado.gen.engine
    def test_redis_storage(self):
        app = self.get_app()
        app.configure_storage("gw_storage_redis.storage.RedisStorage")
        storage = app.storage
        self.storage_tests(storage)
        self.stop()
