# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import time
import os

from configparser import ConfigParser, NoOptionError

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import PluginManager
from alamo_worker.queue import ZeroMQQueue

logger = get_console_logger(__name__)


class WorkerManagement(object):
    """Alamo worker management object."""
    parser = None
    config = None
    message_queue = None

    def __init__(self):
        self.parser = self.build_args()
        self.manager = PluginManager()

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

    @staticmethod
    def init_message_queue(host, port):
        return ZeroMQQueue(host, port)

    @staticmethod
    def send_to_alerter(result):
        logger.info('Sending to Alerter: {}'.format(result))

    def _connect_to_queue(self):
        scheduler_zero_mq_host = self.config.get('zero_mq', 'remote_host')
        scheduler_zero_mq_port = self.config.get('zero_mq', 'remote_port')

        self.message_queue = self.init_message_queue(
            scheduler_zero_mq_host,
            scheduler_zero_mq_port
        )

        self.message_queue.connect()

    def _load_plugins(self):
        try:
            plugins = self.config.get('default', 'plugins').split(',')
        except NoOptionError:
            plugins = []

        # list could have "empty" string ...
        plugins = [plugin for plugin in plugins if plugin]

        assert plugins, 'At least one plugin should be defined in config file.'

        self.manager.load(self.config, plugins)

    def _run(self):
        while True:
            data = self.message_queue.zmq_socket.recv_json()
            start_time = time.time()
            result = self.manager.dispatch(data)
            logger.info("Result received after: {}".format(
                time.time() - start_time)
            )
            self.send_to_alerter(result)

    def execute(self):
        self.parse_config()
        self._load_plugins()
        self._connect_to_queue()
        self._run()


def main():
    management = WorkerManagement()
    management.execute()


if __name__ == '__main__':
    main()
