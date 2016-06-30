# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .request import (
    Request,
)

from .response import (
    Response,
    JsonResponse,
    HtmlResponse,
    TemplateResponse,
    WrappedTemplateResponse,
    FileResponse,
    template_or_json_response,
    wrapped_template_or_json_response,
)

from .gate import (
    Gate,
)

from . import (
    utils,
)

__version__ = '0.2.1'

__package__ = 'poort'
__title__ = 'Poort'
__description__ = 'Poort: The quick gateway.'
__uri__ = 'https://github.com/corverdevelopment/Poort/'

__author__ = 'Nils Corver'
__email__ = 'nils@corverdevelopment.nl'

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2016 Corver Development B.V.'

__all__ = [
    'Request',

    'Response',
    'JsonResponse',
    'HtmlResponse',
    'TemplateResponse',
    'WrappedTemplateResponse',
    'FileResponse',
    'template_or_json_response',
    'wrapped_template_or_json_response',

    'Gate',

    'utils',
]
