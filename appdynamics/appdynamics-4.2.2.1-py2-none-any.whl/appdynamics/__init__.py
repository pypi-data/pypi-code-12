# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import logging
import os.path

from appdynamics.lib import default_log_formatter

# The following is a very basic logging config which outputs WARNING level logs to stderr.
try:
    logger = logging.getLogger('appdynamics')
    level = logging.WARNING
    logger.setLevel(level)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(default_log_formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
except:
    pass


def get_build_filename():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'BUILD.txt')


def get_version(build_file=None, noisy=True):
    try:
        version = []
        build_file = build_file or get_build_filename()

        with open(build_file, 'r') as f:
            for line in f:
                version.append(line.strip().split('=')[-1])
    except:
        if noisy:
            logging.getLogger('appdynamics.agent').exception("Couldn't parse build info.")
        return 'unknown'

    return ' '.join(version)
