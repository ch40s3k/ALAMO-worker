# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
from argparse import ArgumentParser

from mock import MagicMock, patch

from alamo_worker.manage import WorkerManagement
from alamo_worker.plugins import PluginManager


class TestWorker(TestCase):

    @patch('alamo_worker.manage.WorkerManagement.__init__',
           MagicMock(return_value=None))
    def setUp(self):
        self.worker = WorkerManagement()
        self.worker.manager = PluginManager()
        self.worker.parser = WorkerManagement.build_args()

    def _init_config(self, side_effect):
        self.worker.config = MagicMock()
        self.worker.config.get = MagicMock(side_effect=side_effect)

    def test_build_args(self):
        parser = self.worker.build_args()

        self.assertTrue(
            isinstance(parser, ArgumentParser))

    @patch('alamo_worker.manage.PluginManager.load')
    def test_load_plugins_with_empty_plugin_list(self, load_mock):
        self._init_config(['', 'localhost', '2222'])

        with self.assertRaises(AssertionError):
            self.worker._load_plugins()

        self.assertFalse(load_mock.called)

    @patch('alamo_worker.manage.PluginManager.load')
    def test_load_plugins_with_correct_plugin_list(self, load_mock):
        self._init_config(['kairosdb', 'localhost', '2222'])

        self.worker._load_plugins()

        self.assertTrue(load_mock.called)

    @patch('alamo_worker.queue_handler.ZeroMQQueue.connect')
    def test_connect_to_queue(self, queue_mock):

        self._init_config(['localhost', '2222'])
        self.worker._connect_to_queue()
        self.assertTrue(queue_mock.called)
