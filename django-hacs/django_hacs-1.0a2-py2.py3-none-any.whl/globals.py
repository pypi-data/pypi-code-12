# -*- coding: utf-8 -*-
# ++ This file `globals.py` is generated at 3/3/16 6:07 AM ++

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

HACS_APP_NAME = 'hacs'
HACS_APP_LABEL = HACS_APP_NAME
HACS_GENERATED_FILENAME_PREFIX = 'hacs__generated_'
HACS_SERIALIZED_ROUTE_DIR_NAME = 'hacs_routes'


class HACSSiteCache(object):
    """ Obviously this class is not tread safe, infact we don't need to be. """

    def __init__(self):

        """
        :return:
        """
        self.__storage__ = dict()

    def get(self, key, default=None):
        """
        :param key:
        :param default:
        :return:
        """
        return self.__storage__.get(key, default)

    def set(self, key, value):
        """
        :param key:
        :param value:
        :return:
        """
        return self.__storage__.update({key: value})

    def clear(self):
        """
        :return:
        """
        # Not sure it's make sense of performance optimized way
        del self.__storage__
        self.__storage__ = dict()

    def __getitem__(self, item):
        """
        :param item:
        :return:
        """
        return self.__storage__[item]

    def __setitem__(self, key, value):
        """
        :param key:
        :param value:
        :return:
        """
        self.__storage__[key] = value

    def __len__(self):
        """
        :return:
        """
        return len(self.__storage__)

    def __repr__(self):
        """
        :return:
        """
        return repr(self.__storage__)

    def __str__(self):
        """
        :return:
        """
        return str(self.__storage__)


HACS_SITE_CACHE = HACSSiteCache()
