# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import asyncio
import os
from configparser import ConfigParser, NoOptionError

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import PluginManager
from alamo_worker.queue_handler import ZeroMQQueue

logger = get_console_logger(__name__)


class WorkerManagement(object):
    """Alamo worker management object."""
    parser = None
    config = None
    message_queue = None
    task = None

    def __init__(self):
        self.parser = self.build_args()
        self.manager = PluginManager()
        self.parse_config()
        self._load_plugins()
        self._connect_to_queue()

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
    def send_to_alerter(result):
        """Process check with received result to alerter."""
        logger.info('Sending to Alerter: {}'.format(result['integration_key']))

    def _connect_to_queue(self):
        """Establish connection to ALAMO-Scheduler ZeroMQ.
        """
        scheduler_zero_mq_host = self.config.get('zero_mq', 'remote_host')
        scheduler_zero_mq_port = self.config.get('zero_mq', 'remote_port')

        self.message_queue = ZeroMQQueue(scheduler_zero_mq_host,
                                         scheduler_zero_mq_port)
        return self.message_queue.connect()

    def _load_plugins(self):
        """Loads plugins specified in config.py."""
        try:
            plugins = self.config.get('default', 'plugins').split(',')
        except NoOptionError:
            plugins = []

        # list could have "empty" string ...
        plugins = [plugin for plugin in plugins if plugin]

        assert plugins, 'At least one plugin should be defined in config file.'

        self.manager.load(self.config, plugins)

    def start_receiving(self):
        # Wraps task coroutine in a future object
        self.task = asyncio.async(self.receive_data())

    def receive_data(self):
        """Pause function and put it in the back in the event loop.
        It will be called as soon as all other function are executed.
        """
        yield from asyncio.sleep(0)
        data = self.message_queue.zmq_socket.recv_json()
        return data

    @asyncio.coroutine
    def was_received(self):
        self.start_receiving()
        result = yield from self.task
        return result

    def _run(self):
        while True:
            data = yield from self.was_received()
            result = self.manager.dispatch(data)
            self.send_to_alerter(result)

    def execute(self):
        """Initialize asyncio event loop."""
        loop = asyncio.get_event_loop()
        try:
            # return asyncio Task object
            asyncio.async(self._run())
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            loop.close()


def main():
    management = WorkerManagement()
    management.execute()


if __name__ == '__main__':
    main()
