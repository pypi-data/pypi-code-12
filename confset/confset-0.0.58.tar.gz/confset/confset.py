#!/usr/bin/env python
# Copyright (c) 2012-2015, Dwight Hubbard.
# Copyrights licensed under the Apache 2.0 License
# See the accompanying LICENSE.txt file for terms.
"""
Manage package settings
"""
import os
import sys
import shutil
import time
import logging


CONF_PATH = ['/etc/default', '/etc/sysconfig']
METADATA_DIR = '/etc/confset'
logger = logging.getLogger(__name__)


class ConfsetException(Exception):
    pass


class ConfigSettings(object):
    """
    Configuration settings class
    :param conffile:
    """

    def __init__(self, conffile=None):
        self.confpath = config_paths()
        self.conffile = conffile
        self.filename = self.search_for_conf(conffile)
        self.settings, self.order = self.available_settings()
        self.__dict__.update(self.settings)

    # noinspection PyMethodMayBeStatic
    def search_for_conf(self, conffile):
        """
        Search for a configuration file
        :param conffile:
        :return:
        """
        filename = None
        for d in self.confpath:
            filename = os.path.join(d, self.conffile)
            if os.path.isfile(filename) and os.access(filename, os.R_OK):
                break
            else:
                filename = None
        return filename

    def empty_conf_file(self):
        """
        Return a fully filename
        :return:
        """
        for d in self.confpath:
            if os.path.isdir(d) and os.access(d, os.W_OK):
                return os.path.join(d, self.conffile)
        raise ConfsetException(
            'Unable to find a writable configuration directory'
        )   # pragma: no cover

    def available_settings(self):
        """
        Return the settings available in a conf file
        :return:
        """
        comments = []
        order = []
        result_settings = {}
        if self.filename:
            fh = open(self.filename, 'r')
            for line in fh.readlines():
                line = line.strip()
                if line:
                    if line.startswith('#'):
                        temp = line.strip('#').strip()
                        if temp:
                            comments.append(temp)
                    else:
                        if '=' in line:
                            setting = '%s.%s' % (
                                self.conffile, line.split('=')[0])
                            result_settings[setting] = {
                                'help': comments,
                                'value': '='.join(line.split('=')[1:]).strip()
                            }
                            comments = []
                            order.append(setting)
                else:
                    comments = []
        return result_settings, order

    def write_settings(self):
        """
        Commit the current self.settings to disk
        :return:
        """
        if self.filename:
            if os.path.exists(self.filename):
                newname = '%s.confset.%s' % (self.filename, time.strftime("%Y%m%d%H%M%S"))
                logger.debug(
                    'Backing up existing config file: %s to %s', self.filename, newname
                )
                shutil.copy(self.filename, newname)
        else:
            self.filename = self.empty_conf_file()
        logger.debug('Writing to: %s', self.filename)
        if self.filename:
            with open(self.filename, 'w') as file_handle:
                for long_key in self.order:
                    short_key = '.'.join(long_key.split('.')[1:])
                    value = self.settings[long_key].get('value', '')
                    help_text = self.settings[long_key].get('help', [])
                    if isinstance(help_text, str):
                        help_text = help_text.split(os.linesep)
                    logger.debug('Writing: %s=%s' % (short_key, value))
                    if help_text:
                        file_handle.write('\n')
                        for line in help_text:
                            file_handle.write('# %s\n' % line.strip())
                    file_handle.write('{0}={1}\n\n'.format(short_key, value))

    def key_max_column_width(self):
        """
        Determine the max length of the key names
        :return:
        """
        max_len = 1
        for setting in self.settings.keys():
            if len(setting) + len(self.settings[setting]['value']) + 1 > max_len:
                max_len = len(setting) + len(
                    self.settings[setting]['value']) + 1
        return max_len

    def print_settings(
            self, setting_filter=None, sort=False, key_column_width=None,
            info=None
    ):
        """
        Print the current settings
        :param info:
        :param key_column_width:
        :param setting_filter:
        :param sort:
        """
        if sort:
            temp = self.settings.keys()
            temp.sort()
        else:
            temp = self.order

        if key_column_width:
            max_len = key_column_width
        else:
            max_len = self.key_max_column_width()

        for setting in temp:
            if not setting_filter or setting == setting_filter.strip():
                setting_and_value = '%s=%s' % (
                    setting,
                    self.settings[setting]['value']
                )
                if info and self.settings[setting]['help']:
                    print(
                        '%s - %s' % (
                            setting_and_value.ljust(max_len, ' '),
                            self.settings[setting]['help'][0] if self.settings[setting]['help'] else ''
                        )
                    )
                    for line in self.settings[setting]['help'][1:]:
                        print('%s   %s' % ((' ' * max_len), line))
                else:
                    if self.settings[setting]['value']:
                        print(setting_and_value)

    def set(self, key, value, help_text=None):
        """
        Set a setting in a conf file
        :type help_text: list
        :param key:
        :param value
        """
        logger.debug('Setting variable, before: %s', self.settings)
        long_key = '%s.%s' % (self.conffile, key)
        if not help_text:
            if long_key in self.settings.keys():
                help_text = self.settings[long_key].get('help', [])
        if isinstance(help_text, str):
            help_text = help_text.split(os.linesep)
        self.settings.update(
            {
                long_key: {
                    'help': help_text,
                    'value': value
                }
            }
        )
        logger.debug('Setting variable, after: %s', self.settings)
        if long_key not in self.order:
            self.order.append(long_key)
        self.write_settings()

def config_paths():
    """
    Get a list of configuration paths

    Returns
    list
        A list of strings containing full paths to the directories containing
        configuration files.
    """
    global CONF_PATH
    confpath = CONF_PATH
    if hasattr(sys, 'real_prefix') and 'VIRTUAL_ENV' in os.environ.keys():
        venv_path = os.path.join(os.environ['VIRTUAL_ENV'], 'conf')
        if confpath[0] != venv_path:
            confpath.insert(
                0,
                venv_path
            )
    return confpath


def config_files():
    """
    Find all config files
    :return:
    """
    files = []
    for directory in config_paths():
        if os.path.isdir(directory):
            for f in os.listdir(directory):
                if '.confset.' not in f:
                    files.append(f)
    return files


def settings():
    """
    Return all settings as a dictionary
    :return:
    """
    all_settings = {}
    for f in config_files():
        try:
            conf = ConfigSettings(os.path.basename(f))
        except IOError as exc:
            logger.debug(
                'Got %s while getting config settings for %s',
                exc,
                os.path.basename(f)
            )
            continue
        s, o = conf.available_settings()
        all_settings.update(s)
    return all_settings


def print_settings(setting_filter=None, info=False):
    """
    Print settings found
    :param setting_filter:
    :param info:
    """
    configs = []
    max_width = 1
    for f in config_files():
        try:
            conf = ConfigSettings(os.path.basename(f))
        except IOError as exc:
            logger.debug(
                'Got %s while getting config settings for %s',
                exc, os.path.basename(f)
            )
            continue
        if conf.key_max_column_width() > max_width:
            max_width = conf.key_max_column_width()
        configs.append(conf)
    for conf in configs:
        conf.print_settings(
            setting_filter=setting_filter,
            key_column_width=max_width,
            info=info
        )
