# -*- coding: utf-8 -*-


class InvalidStatusCodeError(Exception):
    """ An Invalid status code was returned for this resource """


class MissingUidException(Exception):
    """ A uid attribute was missing! """
