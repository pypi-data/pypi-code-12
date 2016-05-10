# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import logging
import logging.handlers

import os
import errno
#from .system_info import mkdir_p
def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

def get_level_from_string(level_string):
    if (level_string == "DEBUG"):
        return logging.DEBUG
    if (level_string == "INFO"):
        return logging.INFO
    if (level_string == "WARNING"):
        return logging.WARNING
    if (level_string == "ERROR"):
        return logging.ERROR
    if (level_string == "CRITICAL"):
        return logging.CRITICAL

def get_logger():
    from tcell_agent.config import CONFIGURATION
    logging_options = CONFIGURATION.logging_options
    new_logger = logging.getLogger("tcell_agent")
    formatter = logging.Formatter('%(asctime)s - %(name)s -- [%(levelname)s]: %(message)s')

    if (logging_options is None or logging_options.get("enabled",True) == False):
        return None
    
    log_filename = CONFIGURATION.log_filename

    fh = logging.handlers.RotatingFileHandler(
              log_filename, maxBytes=10*1024*1024, backupCount=5)
    fh.setFormatter(formatter)

    new_logger.setLevel(get_level_from_string(logging_options.get("level","INFO")))
    new_logger.addHandler(fh)

    return new_logger

try:
    base_logger
except:
    base_logger = get_logger()
