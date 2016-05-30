#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: log.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: log service

from os.path import sep as SEP
import logging


def get_logger(name, LOG_FILE):
    """Returns a new logger with personalized.
    @param name: logger name
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    ## Redirect log to stdout
    formatter = logging.Formatter("%(levelname)7s | %(lineno)4d  |%(name)15s | %(asctime)s | %(message)s")
    ch = logging.StreamHandler()    # Create console handler and set level to debug
    ch.setLevel(logging.DEBUG)      # Set logging devel
    ch.setFormatter(formatter)      # add formatter to console handler
    log.addHandler(ch)              # add console handler to logger

    # Redirect log to file
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)      # Set logging devel
    log.addHandler(fh)              # add file handler to logger

    return log
