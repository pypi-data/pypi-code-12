# -*- coding: utf-8 -*-
from __future__ import print_function

import contextlib
import io
import malibu
import os
import pprint
import sys

from contextlib import closing
from malibu.config import configuration
from malibu.text import table
from os.path import exists

from malibu.command import module
from malibu.text import ascii
from malibu.util import paths as pathutil


class BuiltinConfigModule(module.CommandModule):

    BASE = "config"

    def __init__(self, loader):

        super(BuiltinConfigModule, self).__init__(base=BuiltinConfigModule.BASE)

        self.__loader = loader

        self.register_subcommand('get', self.config_get)
        self.register_subcommand('init', self.config_init)
        self.register_subcommand('set', self.config_set)
        self.register_subcommand('show', self.config_show)

        # Need to set self._config_paths in any subclasses of this module.
        if not self._config_paths:
            raise AttributeError("Unspecified configuration paths.")

        self._config = None
        self._config_path = ''
        for path in self._config_paths:
            path = pathutil.expand_path(path)
            fdir = pathutil.get_path_base(path)
            if not exists(fdir):
                try:
                    os.mkdir(fdir)
                except:
                    continue
            else:
                if not exists(path):
                    try:
                        with closing(open(path, 'w')) as config:
                            config.write("")
                    except:
                        continue
                if os.access(path, os.R_OK | os.W_OK):
                    self._config_path = path
                    self._config = configuration.Configuration()
                    self._config.load(path)
                else:
                    continue

        if self._config is None:
            paths = ', '.join(self._config_paths)
            raise module.CommandModuleException(
                "Could not open or create configuration file at paths: {}".format(paths))

    def get_configuration(self):
        """ Returns the Configuration instance used by
            this module.
        """

        return self._config

    def config_get(self, *args, **kw):
        """ config:get [section].[key]

            Returns the named variable from the loaded configuration.
        """

        args = args[1:]

        try:
            var_path = args[0]
        except:
            raise module.CommandModuleException("Missing argument(s).")

        var_path = var_path.split('.')
        if len(var_path) > 2:
            var_path = var_path[0:2]

        if len(var_path) == 1:  # Only the section specifier is given
            section_name = var_path[0]
            if not self._config.has_section(section_name):
                print("Unknown configuration section '{}'.".format(
                    ascii.style_text(ascii.FG_GREEN, section_name)))
                return
            else:
                section = self._config.get_section(section_name)
                print("Section [{}]:".format(
                    ascii.style_text(ascii.FG_GREEN, section_name)))
                for key, value in section.items():
                    print("  {} -> {}".format(key, value))
                print
        elif len(var_path) == 2:  # Section and key specifier were given.
            section_name = var_path[0]
            if not self._config.has_section(section_name):
                print("Unknown configuration section '{}'.".format(
                    ascii.style_text(ascii.FG_YELLOW, section_name)))
                return
            else:
                section = self._config.get_section(section_name)
                print("Section [{}]:".format(
                    ascii.style_text(ascii.FG_GREEN, section_name)))
                key = var_path[1]
                value = section.get_string(key, None)
                if not value:
                    value = ascii.style_text(ascii.FG_RED, 'unset')
                print("  {} -> {}".format(key, value))

    def config_do_create(self):
        """ Uses the loaded self._config object to create the bare config for
            the application.
        """

        pass

    def config_init(self, *args, **kw):
        """ config:init []

            Initializes a default configuration in the current config path
            that has been opened.
        """

        try:
            self.config_do_create()
        except Exception as e:
            print("{}".format(
                ascii.style_text(
                    ascii.FG_RED,
                    "Error while creating configuration: {}".format(
                        ascii.style_text(
                            ascii.STYLE_BOLD,
                            str(e))))))

        print("{}".format(
            ascii.style_text(
                ascii.STYLE_BOLD,
                "Configuration initialized at {}.".format(
                    ascii.style_text(
                        ascii.FG_GREEN,
                        self._config_path)))))

        self._config.save(self._config_path)

    def config_set(self, *args, **kw):
        """ config:set [section].[key] [value]

            Sets the named variable in the user configuration.
        """

        args = args[1:]

        try:
            var_path = args[0]
        except:
            raise module.CommandModuleException("Missing argument(s).")

        try:
            var_value = ' '.join(args[1:])
        except:
            raise module.CommandModuleException("Missing argument(s).")

        var_path = var_path.split('.')
        if len(var_path) > 2:
            var_path = var_path[0:2]

        if len(var_path) == 1:  # Only the section specifier is given
            print("Must provide a configuration node in the form of {} to set a value.".format(
                ascii.style_text(ascii.BG_YELLOW, "section.key")))
            return
        elif len(var_path) == 2:  # Section and key specifier were given.
            section_name = var_path[0]
            if not self._config.has_section(section_name):
                print("Unknown configuration section '{}'.".format(
                    ascii.style_text(ascii.FG_YELLOW, section_name)))
                return
            else:
                section = self._config.get_section(section_name)
                print("Section [{}]:".format(
                    ascii.style_text(ascii.FG_GREEN, section_name)))
                key = var_path[1]
                value = section.get_string(key, None)
                if not value:
                    value = ascii.style_text(ascii.FG_RED, 'unset')
                section.set(key, var_value)
                print("  {} => {} -> {}".format(
                    key,
                    ascii.style_text(ascii.FG_RED, value),
                    ascii.style_text(ascii.FG_GREEN, var_value)))

        self._config.save(self._config_path)

    def config_show(self, *args, **kw):
        """ config:show []

            Prints the current configuration.
        """

        for section_name in self._config.sections:
            section = self._config.get_section(section_name)
            print("Section [{}]:".format(
                ascii.style_text(ascii.FG_GREEN, section_name)))
            for key, value in section.items():
                print("  {} -> {}".format(
                    ascii.style_text(ascii.FG_LCYAN, key),
                    ascii.style_text(ascii.FG_LPURPLE, value)))
            print("")
