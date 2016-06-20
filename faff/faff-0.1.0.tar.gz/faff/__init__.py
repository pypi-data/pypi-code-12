#!/usr/bin/env python
# flake8: noqa
# External API.
# Core instance for package information and configuration.
from .core import core
# Main function for command line interface.
from .main import main
# Exceptions for handling.
from .exceptions import (
    FaffException,
    InvalidInputFileException,
    UnknownTargetRuleException,
    InvalidTargetException,
)
# Input file classes.
from .include import Include
from .variable import Variable
from .option import Option
from .targets import (
    Target,
    RuleTarget,
    FileTarget,
)
from .rule import Rule
from .run import Run

__title__ = core.get_name()
__version__ = core.get_version()
__description__ = core.get_description()
__readme__ = 'README.md'
__author__ = 'mojzu'
__email__ = 'mail@mojzu.net'
__requires__ = ()
__data__ = ()
# Test suite uses `Tox`, `nose` and `coverage`.
__test_suite__ = 'nose.collector'
__test_requires__ = (
    'coverage==4.1',
    'nose==1.3.7',
)
