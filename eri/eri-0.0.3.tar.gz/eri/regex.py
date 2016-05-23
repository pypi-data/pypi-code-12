#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: regex.py
Author: zlamberty
Created: 2016-02-16

Description:
    I reuse these regexes all the time...

Usage:
    <usage>

"""

import re

import eri.logging as logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

logger = logging.getLogger(__name__)


# names
_FIRSTNAME = r'[\w\.\s\-\']+'
_SUFFIXES = r'jr|sr|iv|iii|ii|i|v'
_SUFFIX_STUB = r'(?{grouptype:}\b(?:{s:})\b)'
_IS_SUFFIX = _SUFFIX_STUB.format(grouptype=':', s=_SUFFIXES)
_IS_NOT_SUFFIX = _SUFFIX_STUB.format(grouptype='!', s=_SUFFIXES)
_LASTNAME = r'\b(?:{}[\w\.\-\'])+\b'.format(_IS_NOT_SUFFIX)
NAME_REGEX = r'(?P<firstname>{})\s(?P<lastname>{})\s?(?P<suffix>{})?$'.format(
    _FIRSTNAME, _LASTNAME, _IS_SUFFIX
)
