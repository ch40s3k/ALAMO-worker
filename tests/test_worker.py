# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase
from argparse import ArgumentParser

from mock import MagicMock, patch

from alamo_worker.manage import WorkerManagement
from alamo_worker.queue import ZeroMQQueue


class TestWorker(TestCase):
    def setUp(self):
        self.worker = WorkerManagement()

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

    @patch('alamo_worker.queue.zmq.Context')
    def test_init_message_queue(self, context_mock):
        queue = self.worker.init_message_queue('localhost', '2222')
        self.assertTrue(context_mock.called)
        self.assertTrue(isinstance(queue, ZeroMQQueue))

    @patch('alamo_worker.manage.WorkerManagement.init_message_queue')
    def test_connect_to_queue(self, queue_mock):
        z_queue = MagicMock()
        z_queue.connect = MagicMock()
        queue_mock.return_value = z_queue

        self._init_config(['localhost', '2222'])
        self.worker._connect_to_queue()

        queue_mock.assert_called_once_with('localhost', '2222')
        z_queue.connect.assert_called_once_with()

    @patch('alamo_worker.manage.WorkerManagement.parse_config')
    @patch('alamo_worker.manage.WorkerManagement._load_plugins')
    @patch('alamo_worker.manage.WorkerManagement._connect_to_queue')
    @patch('alamo_worker.manage.WorkerManagement._run')
    def test_execute(self, *args):
        run_mock, queue_mock, plug_mock, parse_mock = args

        self.worker.execute()

        self.assertTrue(run_mock.called)
        self.assertTrue(queue_mock.called)
        self.assertTrue(plug_mock.called)
        self.assertTrue(parse_mock.called)
