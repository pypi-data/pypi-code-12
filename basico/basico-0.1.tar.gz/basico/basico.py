#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File: basico.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Main entry point por Basico app
import os
import sys
import traceback as tb
import imp
import signal
from os.path import abspath, sep as SEP
from configparser import SafeConfigParser, ExtendedInterpolation

#~ from gi.repository import GObject

from .log import get_logger
from .gui import GUI
from .iconmanager import IconManager
from .sap import SAP
from .settings import Settings
from .uifuncs import UIFuncs
from .menus import Menus
from .projects import Projects
from .tasks import Tasks
from .plugins import Plugins
from .callbacks import Callback
from .notify import Notification
from .stats import Stats
from .env import ROOT, APP, LPATH, GPATH, FILE


class Basico:
    def __init__(self):
        """Main class: the entry point for Basico.
        It stands for Controller.
        """
        self.__set_env()
        self.log = get_logger(self.__class__.__name__, FILE['LOG'])
        self.log.info("Starting Basico")
        self.__init_config()
        self.services = {}
        try:
            services = {
                'GUI'       :   GUI(),
                'UIF'       :   UIFuncs(),
                'Menus'     :   Menus(),
                'SAP'       :   SAP(),
                'Settings'  :   Settings(),
                'Notify'    :   Notification(),
                'Tasks'     :   Tasks(),
                'IM'        :   IconManager(),
                'Plugins'   :   Plugins(),
                'Callbacks' :   Callback(),
                'Stats'     :   Stats(),
            }
            self.register_services(services)
        except Exception as error:
            self.log.error(error)
            raise


    def __set_env(self):
        # Create local paths if they do not exist
        for DIR in LPATH:
            if not os.path.exists(LPATH[DIR]):
                os.makedirs(LPATH[DIR])


    def __init_config(self):
        #~ self.log.debug("ROOT: %s" % ROOT)
        # Set up config
        CONFIG_FILE = self.get_file('CNF')

        #~ https://docs.python.org/3/library/configparser.html#interpolation-of-values
        self.config = SafeConfigParser(interpolation=ExtendedInterpolation())

        #~ https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.optionxform
        self.config.optionxform = str

        # Save config
        if not os.path.exists(CONFIG_FILE):
            self.log.debug('Configuration file not found. Creating a new one')
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)
            self.log.info('Config file initialited')


    def get_config(self):
        CONFIG_FILE = self.get_file('CNF')
        self.config.read(CONFIG_FILE)

        return self.config


    def get_file(self, name):
        try:
            return FILE[name]
        except:
            self.log.error(self.get_traceback())


    def get_app_info(self, var):
        try:
            return APP[var]
        except:
            return None


    def get_var(self, name, scope='global'):
        if scope == 'global':
            return GPATH[name]
        else:
            return LPATH[name]


    def list_services(self):
        """Return a dictionary of services"""
        return self.services


    def get_service(self, name):
        """Get/Start a registered service
        @type name: name of the service
        @param name: given a service name it returns the associated
        class. If service was not running it is started.
        """
        try:
            service = self.services[name]
            if service.is_started():
                return service
            else:
                service.start(self, name)
                return service
        except KeyError as service:
            self.log.error("Service %s not registered or not found" % service)
            raise

    def register_services(self, services):
        """Register a list of services
        @type services: dict
        @param services: a dictionary of name:class for each service
        """
        for name in services:
            self.register_service(name, services[name])


    def register_service(self, name, service):
        """Register a new service
        @type name: string
        @param name: name of the service
        @type service: class
        @param service: class which contains the code
        """
        try:
            self.services[name] = service
            #~ self.log.debug("Service '%s' loaded successfully" % name)
        except Exception as error:
            self.log.error(error)


    def deregister_service(self, name):
        """Deregister a running service
        @type name: string
        @param name: name of the service
        """
        self.services[name].end()
        self.services[name] = None


    def check(self):
        sap = self.get_service('SAP')
        found = sap.check_webdriver()
        if not found:
            self.log.error("No webdriver found. Exiting.")
        return found


    def stop(self):
        """For each service registered, it executes the 'end' method
        (if any) to finalize them properly.
        """

        # Deregister all services loaded
        self.deregister_service('GUI')

        for name in self.services:
            try:
                self.deregister_service(name)
            except: pass
        # Bye bye
        self.log.info("Basico finished")


    def get_traceback(self):
        return tb.format_exc()


    def run(self):
        try:
            self.gui = self.get_service('GUI')
            #~ self.log.debug("Basico ready to start")
            self.gui.run()
        except:
            self.log.error(self.get_traceback())


def main():
    #DOC: http://stackoverflow.com/questions/16410852/keyboard-interrupt-with-with-python-gtk
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    basico = Basico()
    run = True #basico.check()
    if run:
        basico.run()
    sys.exit(0)
