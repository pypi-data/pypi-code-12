#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from sys import exit
from metzoo import lib

from collections import namedtuple
Plugin = namedtuple('Plugin', ['name', 'config', 'module'])


class FuckPip(object):
    def __init__(self, name):
        self.name = name

    def debug(self, msg):
        print 'DEBUG {} {}'.format(self.name, msg)

    def error(self, msg):
        print 'ERROR {} {}'.format(self.name, msg)


def init_logger(name, filename):
    return FuckPip(name)

# def init_logger(name, filename):
#     LOG_FORMAT = "%(asctime)-15s %(levelname)9s  %(filename)s:%(lineno)s %(message)s"
#     logging.basicConfig(filename=filename, level=logging.DEBUG, format=LOG_FORMAT)
#
#     logger = logging.getLogger(name)
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.DEBUG)
#     console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
#     logger.addHandler(console_handler)

#     return logger


def validate_config(name, config_dict, logger, properties):
    for p in properties:
        if lib.config.get(config_dict, p) is None:
            logger.error("invalid configuration for '{}': '{}' property not found".format(name, p))
            exit(-4)


def init_config(filename, logger):
    logger.debug("initializing configuration '{}'".format(filename))
    config_dict = None
    try:
        config_dict = lib.config.load_yaml_dict(filename)
    except IOError as e:
        logger.error("can't load '{}': {}".format(filename, e))
        exit(-3)

    validate_config(filename, config_dict, logger, ["plugins"])

    logger.debug("configuration loaded")
    return config_dict


def init_db(filename, logger):
    logger.debug("initializing db '{}'".format(filename))
    try:
        db = lib.DB(filename)
    except Exception as ex:
        logger.error("can't connect to '{}' db: {}".format(filename, ex))
        exit(-2)
    else:
        logger.debug("connected to '{}' db".format(filename))

    return db


# imports have 2 forms:
#
#   (1) import A -> (A, [])
#   (2) from B import C -> (B, [C])
#
def parseimport(import_stmt, logger):
    try:
        import re
        m = re.search('from (.*) import (.*)', import_stmt)
        return (m.group(1), m.group(2).split(","))
    except AttributeError:
        m = re.search('import (.*)', import_stmt)
        if m is None:
            logger.debug("can't decode '{}'".format(import_stmt))
            return None
        return (m.group(1), [])


def load_module(package, import_stmt, logger):
    logger.debug("loading module '{}'".format(import_stmt))

    name, fromlist = parseimport(import_stmt, logger)
    if len(fromlist) > 1:
        raise ImportError("'{}' must have only 1 imported name as in 'from X import Y' not 'from X import Y, Z'".format(import_stmt))

    module = __import__(name, globals(), locals(), fromlist, -1)
    if len(fromlist) == 1:
        if fromlist[0] in dir(module):
            module = getattr(module, fromlist[0])
        else:
            raise ImportError("module '{}' not found in '{}'".format(fromlist[0], name))

    if "read" not in dir(module):
        raise ImportError("function 'read' not found in {}".format(import_stmt))

    return module


def install_package(repository, package, logger):
    logger.debug("installing '{}'".format(package))
    import pip
    pip.main(["install", "--upgrade", "-i", repository, package])


def load(repository, package, import_stmt, logger):
    try:
        module = load_module(package, import_stmt, logger)
    except ImportError:
        install_package(repository, package, logger)
        module = load_module(package, import_stmt, logger)

    return module


def init_plugins(config_dict, logger):
    logger.debug("loading plugins")
    plugins = []
    plugins_config = lib.config.get(config_dict, "plugins")
    repository = lib.config.get(config_dict, "repository", "https://pypi.python.org/pypi")
    for plugin_name, plugin_config in plugins_config.iteritems():
        validate_config(plugin_name, plugin_config, logger, ["module", "module.package", "module.import"])
        package = lib.config.get(plugin_config, "module.package")
        import_stmt = lib.config.get(plugin_config, "module.import")
        plugin_repository = lib.config.get(plugin_config, "module.repository")
        try:
            package_repository = plugin_repository or repository
            module = load(package_repository, package, import_stmt, logger)
            plugins.append(Plugin(plugin_name, plugin_config, module))
        except Exception as e:
            logger.error("can't load '{}': {}".format(plugin_name, e))

    logger.debug("plugins: {}".format(plugins))
    return plugins


def read(config_file, db_file, log):
    logger = init_logger("metzoo-reader", log)
    logger.debug("============================== start ==============================")

    config_dict = init_config(config_file, logger)
    db = init_db(db_file, logger)
    plugins = init_plugins(config_dict, logger)

    for plugin in plugins:
        logger.debug("reading from plugin '{}'".format(plugin.name))
        read_data = plugin.module.read(plugin.config, logger)
        logger.debug("read {} from {}".format(read_data, plugin.name))
        db.save_all(read_data)

    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


def main():
    program = "metzoo-reader"

    import argparse
    parser = argparse.ArgumentParser(prog=program)

    parser.add_argument("--config", type=str, default="{}.yaml".format(program),
                        help="YAML file to load as configuration")

    parser.add_argument("--db", type=str, default="{}.db".format(program),
                        help="Local sqlite3 database to save data that couldn't be sent")

    parser.add_argument("--log", type=str, default="{}.log".format(program),
                        help="Log file to append logs")

    args = parser.parse_args()
    read(args.config, args.db, args.log)

if __name__ == "__main__":
    main()
