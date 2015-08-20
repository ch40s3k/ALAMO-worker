# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import plugin
from alamo_worker.plugins import BasePlugin

logger = get_console_logger(__name__)


@plugin
class KairosDBPlugin(BasePlugin):
    _type = 'kairosdb'

    def execute(self, check):
        logger.info('KairosDB: {}'.format(check))
