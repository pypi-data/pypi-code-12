# clustercron/config.py
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os.path

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

_config = {
    'cache': {
        'filename': '/tmp/clustercron_cache.json',
        'expire_time': 59,
        'max_iter': 20,
    }
}


def _update_config_from_conf():
    basename = 'clustercron.ini'
    filenames = (
        os.path.join('/etc/', basename),
        os.path.join(os.path.expanduser("~"), '.' + basename)
    )
    parser = configparser.ConfigParser()
    for filename in filenames:
        if parser.read(filename) == [filename]:
            for section in parser.sections():
                try:
                    for key, value in parser.items(section):
                        try:
                            if _config[section].get(key, None) is not None:
                                _config[section][key] = value
                        except AttributeError:
                            break
                except configparser.NoSectionError:
                    pass

_update_config_from_conf()
for key, value in _config.items():
    globals()[key] = value
