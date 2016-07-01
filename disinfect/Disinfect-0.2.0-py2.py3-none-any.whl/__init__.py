from __future__ import absolute_import, division, print_function

from .disinfect import (
    Field,
    MappedValueError,
    Mapping,
    MultiValueError,
    Test,
    test_and_return,
    validate,
    sanitize,
)

from .tests import (
    Boolean,
    Date,
    DateTime,
    Email,
    Enum,
    Float,
    InstanceOf,
    Int,
    List,
    ListOf,
    Regex,
    Set,
    String,
    Upload,
)

__version__ = '0.2.0'

__package__ = 'disinfect'
__title__ = 'Disinfect'
__description__ = 'Disinfect: Destroy bad input.'
__uri__ = 'https://github.com/corverdevelopment/Disinfect/'

__author__ = 'Nils Corver'
__email__ = 'nils@corverdevelopment.nl'

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2016 Corver Development B.V.'

__all__ = [
    'Field',
    'MappedValueError',
    'Mapping',
    'MultiValueError',
    'Test',
    'test_and_return',
    'validate',
    'sanitize',

    'Boolean',
    'Date',
    'DateTime',
    'Email',
    'Enum',
    'Float',
    'InstanceOf',
    'Int',
    'List',
    'ListOf',
    'Regex',
    'Set',
    'String',
    'Upload',
]
