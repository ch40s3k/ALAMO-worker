# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import plugin
from alamo_worker.plugins import BasePlugin

logger = get_console_logger(__name__)


@plugin
class KairosDBPlugin(BasePlugin):
    _type = 'kairosdb'
    _endpoint = '/api/v1/datapoints/query'

    def execute(self, check):

        result = None

        if self._cfg['host'].startswith('http://') or \
                self._cfg['host'].startswith('https://'):

            endpoint = "{}:{}{}".format(self._cfg['host'],
                                        self._cfg['port'],
                                        self._endpoint)

        else:
            endpoint = "http://{}:{}{}".format(self._cfg['host'],
                                               self._cfg['port'],
                                               self._endpoint)
        try:

            response = requests.post(
                endpoint,
                data=json.dumps(check.get('query'), ''),
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()
            result = self.process(check, data)

        except (ValueError,
                requests.exceptions.RequestException) as e:
            result = None
            logger.error(e)

        return result

    @staticmethod
    def process(check=None, data=None):

        check['result'] = data.get('queries', '')
        return check
