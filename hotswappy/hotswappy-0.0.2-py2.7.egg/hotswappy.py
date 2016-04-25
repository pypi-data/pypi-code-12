import inspect
import logging


class Plugin(object):
    """The base plugin object.

    All plugins must inherit from this class
    to be seen by the controller.
    """
    name = None


class Controller(object):

    def __init__(self, module):
        self.module = module
        self.plugins = {}

    def load(self, name=None):
        """Load one or more plugins.
        """
        modules = inspect.getmembers(self.module, inspect.ismodule)
        classes = [
            _class[1]
            for module in modules
            for _class in inspect.getmembers(module[1], inspect.isclass)
            if issubclass(_class[1], Plugin)]

        if name:
            classes = [c for c in classes if c.name == name]

        for _class in classes:
            self.plugins[_class.name] = _class()

    def hotswap(self, name=None):
        """Reload one or more plugins.

        """
        self.plugins = {}
        plugins = inspect.getmembers(self.module, inspect.ismodule)
        
        for plugin in plugins:
            reload(plugin[1])
        
        self.load(name)
