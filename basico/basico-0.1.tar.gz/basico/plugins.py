#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: hooks.py
# Author: Tomás Vírseda
# License: GPL v3
# Description:  a simple plugin system based on hooks

import os

import pkg_resources

from .service import Service

ENTRYPOINT = 'basico.plugins'

class Plugins(Service):
    def initialize(self):
        self.blacklist = set()
        self.rebuild_plugins()
        self.plugins = self.init_plugins()


    def __len__(self):
        return len(self.plugins)


    def get_services(self):
        pass


    def rebuild_local_plugins(self):
        #~ print GPATH['PLUGINS']
        for plugindir in os.listdir(LPATH['PLUGINS']):
            setupdir = LPATH['PLUGINS'] + '/' + plugindir
            setupfile = LPATH['PLUGINS'] + '/' + plugindir + '/setup.py'
            #~ print (setupfile)
            if os.path.exists(setupfile):
                cmd = "cd %s; python %s develop --install-dir .. -m" % (setupdir, setupfile)
                (exitstatus, outtext) = commands.getstatusoutput(cmd)
                if exitstatus != 0:
                    self.log.warning( "Plugin '%s' not available. Error: %d" % (plugindir, exitstatus) )
                    self.log.warning( outtext )


    def rebuild_plugins(self):
        DIR_PLUGINS = self.get_var('PLUGINS', 'local')
        self.log.debug("Looking for plugins in: %s" % DIR_PLUGINS)
        for plugindir in os.listdir(DIR_PLUGINS):
            setupdir = DIR_PLUGINS + '/' + plugindir
            setupfile = DIR_PLUGINS + '/' + plugindir + '/setup.py'
            if os.path.exists(setupfile):
                cmd = "cd %s; python3 %s develop --install-dir .. -m > /dev/null 2>&1" % (setupdir, setupfile)
                exitstatus = os.system(cmd)
                #~ (exitstatus, outtext) = commands.getstatusoutput(cmd)
                self.log.debug(exitstatus)
                if exitstatus != 0:
                    self.log.warning( "Plugin '%s' not available. Error: %d" % (plugindir, exitstatus) )
                    #~ self.log.warning( outtext )


    def init_plugins(self):
        """
        Load local and system hooks.
        """
        DIR_PLUGINS = self.get_var('PLUGINS')
        plugins = {}

        # Load local plugins
        pkg_resources.working_set.add_entry(DIR_PLUGINS)
        pkg_env = pkg_resources.Environment([DIR_PLUGINS])
        loaded = 0
        for name in pkg_env:
            egg = pkg_env[name][0]
            egg.activate()
            modules = []
            for name in egg.get_entry_map(ENTRYPOINT):
                try:
                    entry_point = egg.get_entry_info(ENTRYPOINT, name)
                    cls = entry_point.load()
                    cls.app = self.app
                    #~ print dir(cls)
                    if not hasattr(cls, 'capabilities'):
                        cls.capabilities = []
                    instance = cls()
                    for c in cls.capabilities:
                        plugins.setdefault(c, []).append(instance)
                    loaded = loaded + 1
                except Exception as error:
                    self.log.warning( "Hook '%s': %s" % (name, error))
                    raise

        self.log.debug("Plugin system initialited: %d plugins loaded" % loaded)
        return plugins


    def get_plugin_by_key(self, key):
        for plugin in self.get_all_plugins():
            if plugin.key == key:
                return plugin

        return None


    def get_plugins_by_capability(self, capability):
        try:
            plist = []
            for plugin in self.plugins.get(capability, []):
                active = self.get_active(plugin.key)
                if active:
                    plist.append(plugin)
            return plist
            #~ return self.plugins.get(capability, [])
        except Exception as error:
            self.log.error( error )


    def get_all_plugins(self):
        result = set()
        for p in self.plugins.itervalues():
            for plugin in p:
                result.add(plugin)
        return list(result)


    def get_plugin_path(self, plugin_key):
        DIR_PLUGINS = self.get_var('PLUGINS')
        return DIR_PLUGINS + '/' + plugin_key


    def get_active(self, plugin_key):
        mark = self.get_disabled_mark(plugin_key)
        if os.path.exists(mark):
            return False
        else:
            return True


    def disable(self, plugin_key):
        try:
            mark = self.get_disabled_mark(plugin_key)
            open(mark, 'w').close()
            self.blacklist.add(plugin_key)
        except:
            pass


    def enable(self, plugin_key):
        mark = self.get_disabled_mark(plugin_key)
        try:
            os.remove(mark)
            self.blacklist.remove(plugin_key)
        except:
            pass


    def get_disabled_mark(self, plugin_key):
        return self.get_plugin_path(plugin_key) + '/DISABLED'


    def get_blacklist(self):
        return self.blacklist
