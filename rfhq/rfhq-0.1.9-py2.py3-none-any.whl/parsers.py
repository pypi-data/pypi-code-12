# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from pandas import json
from django.conf import settings
from django.utils import six
from rest_framework.parsers import BaseParser
from rest_framework.exceptions import ParseError


class LineDelimitedJSONParser(BaseParser):
    """
    Parses Line Delimited JSON-serialized data.
    """

    media_type = 'application/x-ldjson'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as Line Delimited JSON and returns the resulting data.

        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        return [self.parse_line(line, encoding) for line in stream]

    def parse_line(self, line, encoding):
        try:
            return json.loads(line.decode(encoding))
        except ValueError as exc:
            raise ParseError('Line delimited JSON parse error - %s' % six.text_type(exc))
