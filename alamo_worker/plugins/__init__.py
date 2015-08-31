# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from configparser import NoSectionError

from alamo_worker.logger import get_console_logger

logger = get_console_logger(__name__)


class BasePlugin(object):
    """Base plugin implementation.

    ``_type`` is used to determine type of the plugin.
    ``_cfg`` keeps plugin configuration.
    """
    _type = None
    _cfg = None

    def __init__(self):
        if self._type is None:
            msg = ('Class ``{}`` does not provide '
                   '"_type" attribute.').format(self.__class__.__name__)

            raise NotImplementedError(msg)

    def init(self, cfg):
        self._cfg = cfg

    def execute(self, check):
        raise NotImplementedError()


class PluginManager(object):
    """Plugin manager for alamo worker.
    This class always return the same object (Singleton pattern).

    ``_plugins`` keeps plugin objects
    ``_classes`` keeps plugin (class) reference to loaded plugin
    """
    _plugins = {}
    _classes = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(PluginManager, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def _import_plugins(self, plugins):
        """When specific plugins being imported
        ``@plugin`` decorator registers just class reference.
        """
        for _plugin in plugins:
            __import__('alamo_worker.plugins.{}'.format(_plugin),
                       fromlist=['*'])

    def _instantiate_plugins(self, config):
        """Instantiate loaded plugins.

        :param config: Config object
        """
        for plugin_type, plugin_cls in self._classes.items():
            instance = plugin_cls()
            try:
                _plug_cfg = dict(config.items(plugin_type))
            except NoSectionError:
                _plug_cfg = {}

            logger.info('Loading config for plugin "{}": {}'.format(
                plugin_type, _plug_cfg)
            )

            instance.init(_plug_cfg)

            self._plugins[plugin_type] = instance

    def load(self, config, plugins):
        """Load and instantiate plugins.

        :param config: Config object
        :param plugins: plugin list
        """
        self._import_plugins(plugins)
        self._instantiate_plugins(config)

    def register(self, cls):
        """Register reference to plugin class.
        It must be subclass of BasePlugin.

        :type cls: class
        """
        if not issubclass(cls, BasePlugin):
            logger.error(
                'Class ``{}`` is not subclass of ``{}``.'.format(
                    cls.__name__,
                    BasePlugin.__name__)
            )
            return

        if cls._type in self._classes:
            logger.warn('Plugin "{}" already registered.'.format(cls))
        else:
            logger.info('Plugin "{}" registered successfully.'.format(
                cls.__name__)
            )
            self._classes[cls._type] = cls

    def dispatch(self, payload):
        """Dispatch which of available plugins should perform
        data processing.

        :param dict payload:
        """
        _plugin = payload.get('type')
        try:
            _plugin = self._plugins[_plugin]
            ret = _plugin.execute(payload)
        except KeyError:
            ret = None
            logger.error('Could not find plugin ``{}``.'.format(_plugin))

        return ret


def plugin(cls):
    """A decorator to create plugin classes::

        @plugin
        class MyPlugin(BasePlugin):
            pass

    Each time plugin discovers new plugin it will register *reference* to
    plugin class in ``PluginManager`` instance (which is Singleton object).

    :type cls: class
    :rtype: class
    """
    manager = PluginManager()

    manager.register(cls)

    return cls
