# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from mock import patch

from alamo_worker.plugins import plugin


class PluginDecoratorTest(TestCase):
    @patch('alamo_worker.plugins.PluginManager.register')
    def test_me(self, register_mock):
        class Fake(object):
            pass

        plugin(Fake)

        self.assertTrue(register_mock.called)
