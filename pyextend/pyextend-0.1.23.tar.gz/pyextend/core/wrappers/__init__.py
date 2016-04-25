# coding: utf-8
"""
    pyextend.core.wrappers
    ~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers packages

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

from .singleton import singleton
from .accepts import accepts
from .timethis import timethis
from .timeout import timeout
from . import system as sys

__all__ = ['singleton', 'accepts', 'timethis', 'timeout', 'sys']
