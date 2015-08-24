# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from mock import MagicMock, patch

from alamo_worker.logger import get_console_logger
from alamo_worker.plugins import PluginManager, BasePlugin, plugin

logger = get_console_logger(__name__)


@plugin
class TestPlugin(BasePlugin):
    _type = 'test'

    def execute(self, *args):
        pass


class PluginManagerTest(TestCase):
    def setUp(self):
        self.test_manager = PluginManager()
        self.config = MagicMock()
        self.config.items = MagicMock(return_value=[('a', 'a')])

    def test_singletons(self):
        b = PluginManager()

        self.assertEqual(id(self.test_manager), id(b))

    def test_plugin_instantiation(self):
        # test plugin already registered
        self.test_manager._instantiate_plugins(self.config)

        self.assertTrue(
            isinstance(self.test_manager._plugins['test'], TestPlugin))
        self.assertFalse(
            isinstance(self.test_manager._classes['test'], TestPlugin))

    @patch('alamo_worker.plugins.logger.warn')
    def test_re_register(self, logger_mock):
        self.test_manager.register(TestPlugin)

        self.assertTrue(logger_mock.called)

    @patch('alamo_worker.plugins.logger.error')
    def test_plugin_subclass(self, logger_mock):
        class Fake(object):
            pass

        self.test_manager.register(Fake)
        self.assertTrue(logger_mock.called)

    @patch('alamo_worker.plugins.tests.test_plugin_manager.TestPlugin.execute')
    def test_dispatch(self, execute):
        payload = {
            'type': 'test',
            'foo': 'foo',
            'bar': 'bar'
        }
        self.test_manager._instantiate_plugins(self.config)
        self.test_manager.dispatch(payload)

        self.assertTrue(execute.called)
