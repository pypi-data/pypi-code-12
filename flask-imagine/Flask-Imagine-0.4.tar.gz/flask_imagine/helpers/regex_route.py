"""
This module implemented a Regexp route handler.
"""
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    """
    Regexp url converter.
    """
    def __init__(self, url_map, *items):
        """
        :param url_map:
        :param items:
        :return:
        """
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
