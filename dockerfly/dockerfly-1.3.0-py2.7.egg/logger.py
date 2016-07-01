#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import os
import logging

from dockerfly.settings import LOG_ROOT

_fh = logging.FileHandler(os.path.join(LOG_ROOT, 'dockerflyd.log'))

def getLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _fh.setFormatter(formatter)
    logger.addHandler(_fh)
    return logger

def getFh():
    return _fh

