import os
import importlib


def plugins_dir():
    return os.path.dirname(os.path.realpath(__file__))


def import_plugin(plugin_name):
    plugin_import = importlib.import_module(__name__ + '.' + plugin_name)
    plugin_import = reload(plugin_import)
    return plugin_import

