# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import plugin
from alamo_worker.plugins import BasePlugin

logger = get_console_logger(__name__)


@plugin
class GraphitePlugin(BasePlugin):
    _type = 'graphite'

    def execute(self, check):
        logger.info('Graphite: {}'.format(check))
