# -*- coding: utf-8 -*-


class BadURLException(Exception):
    """ An Invalid URL was parsed """


class InvalidStatusCodeError(Exception):
    """ An invalid status code was returned for this resource """


class MissingUidException(Exception):
    """ A uid attribute was missing! """
