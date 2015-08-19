# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import os
from configparser import ConfigParser

from alamo_worker.logger import get_console_logger

logger = get_console_logger(__name__)


class WorkerManagement(object):
    """Alamo worker management object."""
    parser = None
    config = None

    def __init__(self):
        self.parser = self.build_args()

    @staticmethod
    def build_args():
        """Build management arguments."""
        parser = argparse.ArgumentParser()

        parser.add_argument(
            '--config', '-c',
            type=str,
            required=False,
            help=(
                'Provide config file for Alamo worker. '
                'If not provided default config file will be taken.'
            )
        )
        return parser

    def parse_config(self):
        """Parse config file."""
        args = self.parser.parse_args()
        config_file = args.config or os.path.join(
            os.path.dirname(__file__),
            'config.cfg'
        )

        self.config = ConfigParser()
        self.config.read(config_file)

    def execute(self):
        self.parse_config()

        zero_mq_host = self.config.get('zero_mq', 'remote_host')
        zero_mq_port = self.config.get('zero_mq', 'remote_port')

        logger.info(zero_mq_host)
        logger.info(zero_mq_port)


def main():
    management = WorkerManagement()
    management.execute()
