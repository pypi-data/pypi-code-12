# coding: utf-8

"""
    trophyfetcher.logger
    ~~~~~~~~~~~~~~~~~~~~

    This module implements the logger of errors and warnings for TrophyFetcher.

    :copyright: (c) 2016 by Roberto Soares
    :license: MIT
"""

from . import config

from datetime import datetime


def log(message):
    errors = open(config.PATH_TO_LOG, 'a')
    errors.write(message + ' ' + datetime.now().strftime(config.DATETIME_FORMAT) + '\n')
    errors.close()
