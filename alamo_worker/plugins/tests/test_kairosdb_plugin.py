# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime
from unittest import TestCase

import responses

from requests.exceptions import ConnectionError

from alamo_worker.plugins.kairosdb import KairosDBPlugin

TEST_QUERY = {
    "metrics": [
        {
            "tags": {"host": "example.com", "domain": "tech",
                     "context": "test"},
            "name": "kairosdb.datastore.cassandra.key_query_time",
            "group_by": [
                {
                    "name": "tag",
                    "tags": [
                        "query_index"
                    ]
                }
            ],
            "aggregators": [
                {
                    "name": "sum",
                    "align_sampling": True,
                    "sampling": {
                        "value": "1",
                        "unit": "seconds"
                    }
                }
            ]
        }
    ],
    "cache_time": 0,
    "start_relative": {
        "value": "1",
        "unit": "hours"
    }
}

TEST_CHECK = {
    "name": "check_test",
    "interval": 10,
    "type": "kairosdb",
    "query": TEST_QUERY,
    "debounce": 1,
    "tags": {"tag1": "value1", "tag2": "value2", "tag3": "value3"},
    "threshold_value": 100,
    "operator": ">",
    "severity": "warning",
    "integration_key": "some_unique_key_1",
    "last_run": datetime.timestamp(datetime.now()),
}


class TestKairosdbPlugin(TestCase):

    def setUp(self):
        self.kairosdb = KairosDBPlugin()
        self.cfg = {'host': 'localhost', 'port': '2222'}
        self.kairosdb.init(self.cfg)
        self.endpoint = "http://{}:{}{}".format(self.kairosdb._cfg['host'],
                                                self.kairosdb._cfg['port'],
                                                self.kairosdb._endpoint)
        self.test_check_kairos = TEST_CHECK

    @responses.activate
    def test_execute(self):

        responses.add(responses.POST, self.endpoint,
                      body=json.dumps({'queries': [{'result': 'test'}]}),
                      content_type='application/json')

        response = self.kairosdb.execute(self.test_check_kairos)

        self.assertListEqual(response['result'], [{'result': 'test'}])

    @responses.activate
    def test_execute_http_error(self):

        responses.add(responses.POST, self.endpoint, status=404,
                      body=json.dumps({}),
                      content_type='application/json')

        response = self.kairosdb.execute(self.test_check_kairos)

        self.assertIsNone(response)

    @responses.activate
    def test_execute_connection_error(self):

        exception = ConnectionError("ConnectionError")
        responses.add(responses.POST, self.endpoint,
                      body=exception,
                      content_type='application/json')

        response = self.kairosdb.execute(self.test_check_kairos)
        self.assertIsNone(response)
