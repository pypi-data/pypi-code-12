# -*- coding: utf-8 -*-
import os

KARABINER_APP_PATH = '/Applications/Karabiner.app'
DEFAULT_CONFIG_PATH = '~/.easy_karabiner.py'
DEFAULT_OUTPUT_PATH = '~/Library/Application Support/Karabiner/private.xml'

command_options = {}


def set(options):
    command_options.update(options)


def get(key):
    return command_options.get(key)


def get_default_config_path():
    return os.path.expanduser(DEFAULT_CONFIG_PATH)


def get_default_output_path():
    return os.path.expanduser(DEFAULT_OUTPUT_PATH)


def get_data_dir():
    return os.path.join(os.path.dirname(__file__), 'data')


def get_data_path(filename):
    return os.path.join(get_data_dir(), filename)


def get_karabiner_app_path():
    return KARABINER_APP_PATH


def _get_path_relate_to_karabiner(relative_path):
    return os.path.join(get_karabiner_app_path(), relative_path)


def get_karabiner_bin_dir():
    return _get_path_relate_to_karabiner('Contents/Library/bin')


def get_karabiner_resources_dir():
    return _get_path_relate_to_karabiner('Contents/Resources')


def get_karabiner_bin(filename):
    return os.path.join(get_karabiner_bin_dir(), filename)
