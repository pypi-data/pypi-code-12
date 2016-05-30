#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: service.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Service class

import sys

from .log import get_logger


class Service(object):
    """
    Service class is the base class for the rest of main classes used in
    the application.
    Different modules (GUI, Database, Ask, etc...) share same methods
    which is useful to start/stop them, simplify logging and, comunicate
    each other easily.
    """

    def __init__(self, app=None):
        """Initialize Service instance
        @type app: Basico instance
        @param app: current Basico instance reference
        """
        self.started = False


    def is_started(self):
        """Return True or False if service is running / not running
        """
        return self.started


    def start(self, app, logname=None):
        """Start service.
        Use initialize for writting a custom init method
        @type app: basico
        @param app: basico Class pointer.
        @type logname: string
        @param logname: name of associated logger. It is used aswell to
        identify configuration section name
        """
        self.started = True
        self.app = app
        logfile = self.app.get_file('LOG')
        self.log = get_logger(logname, logfile)
        self.config = self.app.get_config()
        self.section = logname
        self.init_section(logname)

        try:
            self.initialize()
            self.log.debug("Service %s loaded" % logname)
        except Exception as error:
            self.log.error (self.get_traceback())


    def get_var(self, name, scope='global'):
        return self.app.get_var(name, scope)


    def get_app_info(self, name):
        return self.app.get_app_info(name)


    def get_file(self, name):
        return self.app.get_file(name)


    def end(self):
        """End service
        Use finalize for writting a custom end method
        """
        self.started = False
        try:
            self.finalize()
        except Exception as error:
            self.log.error (self.get_traceback())


    def initialize(self):
        """Initialize service.
        All clases derived from Service class must implement this method
        """
        pass


    def finalize(self):
        """Finalize service.
        All clases derived from Service class must implement this method
        """
        pass


    def get_config_value(self, key):
        """Get value for a given param in section for this service
        @type param: string
        @param param: parameter name
        """
        self.config = self.app.get_config()
        if self.config.has_section(self.section):
            if self.config.has_option(self.section, key):
                return self.config.get(self.section, key)

        return None


    def set_config_value(self, key, value):
        """Set value for a given param in section for this service
        @type param: string
        @param param: parameter name
        @type value: string
        @param param: new value for this parameter
        """
        self.config[self.section][key] = value
        self.log.debug("CONFIG[%s][%s] = %s" % (self.section, key, value))
        self.save_config()


    def init_section(self, section):
        """Check if section exists in config. If not, create it"""
        if not self.config.has_section(section):
            self.config.add_section(section)
            self.log.debug("CONFIG[%s] section created" % section)
        self.save_config()


    def save_config(self):
        CONFIG_FILE = self.get_file('CNF')
        with open(CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)
            #~ self.log.debug('Configuration file save')


    def get_traceback(self):
        return self.app.get_traceback()


    def get_service(self, name):
        return self.app.get_service(name)
