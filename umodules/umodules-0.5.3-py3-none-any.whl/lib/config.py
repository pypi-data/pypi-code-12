import logging
import os

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager

# from .commands.command import ICommand
# from .modules.module import IModule

from command import ICommand
from umodules.lib.modules.module import IModule


class Config(object):

    def __init__(self):
        self.manager = PluginManager()

    def load_plugins(self):
        """
        Returns a Dictionary of Module Plugins

        :return: A Dictionary of Modules
        """

        #   create plugin manager and set categories
        self.manager.setCategoriesFilter({
            "Default": IPlugin,
            "Modules": IModule,
            "Commands": ICommand,
        })

        #   build path to modules
        this_dir = os.path.abspath(os.path.dirname(__file__))
        module_plugin_dir = os.path.join(this_dir, 'modules')
        command_plugin_dir = os.path.join(this_dir, 'commands')
        places = [module_plugin_dir, command_plugin_dir]
        self.manager.setPluginPlaces(places)

        logging.debug("- searching for plugins at {0}".format(places))

        #   our default extension is '.plugin'
        self.manager.setPluginInfoExtension("plugin")

        #   collect all plugins
        self.manager.collectPlugins()

        #   activate and initialize all module plugins
        for pluginInfo in self.manager.getAllPlugins():
            self.manager.activatePluginByName(pluginInfo.name)
            logging.debug("- plugin [{0}] has been activate".format(pluginInfo.name))
            module = pluginInfo.plugin_object
            module.plugin_name = pluginInfo.name

    def get_modules(self):
        return self.manager.getPluginsOfCategory("Modules")

    def get_commands(self):
        return self.manager.getPluginsOfCategory("Commands")

    def load_tokens(self):
        pass




