# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests

from requests.exceptions import ConnectionError, HTTPError

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import plugin

from alamo_worker.plugins import BasePlugin

logger = get_console_logger(__name__)


@plugin
class KairosDBPlugin(BasePlugin):
    _type = 'kairosdb'
    _endpoint = '/api/v1/datapoints/query'

    def execute(self, check):
        endpoint = "http://{}:{}{}".format(self._cfg['host'],
                                           self._cfg['port'],
                                           self._endpoint)
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(check.get('query'), ''),
                timeout=300
            )
            response.raise_for_status()
            data = response.json()
            ret = self.process(check, data)

        except (ValueError, HTTPError) as e:
            ret = None
            logger.error(e)

        except ConnectionError as e:
            ret = None
            logger.error(e)

        return ret

    @staticmethod
    def process(check=None, data=None):

        check['result'] = data.get('queries', '')
        return check
