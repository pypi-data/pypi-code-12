# -*- coding: utf-8 -*-
from __future__ import print_function
from .fucking_string import ensure_utf8


class NeedOverrideError(NotImplementedError):
    def __init__(self, errmsg='You need override this method'):
        super(NeedOverrideError, self).__init__(self, errmsg)


class ConfigError(Exception):
    pass


class ConfigWarning(Exception):
    pass


class InvalidDefinition(ConfigWarning):
    pass


class InvalidKeymapException(ConfigWarning):
    pass


class UndefinedFilterException(ConfigWarning):
    pass


class UndefinedKeyException(ConfigWarning):
    pass


class ExceptionRegister(object):
    """This class is used to record the occurrence of any exceptions,
    so we can provide a user friendly error message.
    """
    error_table = {}
    raw_maps_table = {}

    @classmethod
    def put(cls, k, raw_map):
        k = ensure_utf8(k)
        if k not in cls.raw_maps_table:
            cls.raw_maps_table[k] = raw_map

    @classmethod
    def record_by(cls, k, exception):
        k = ensure_utf8(k)
        raw_map = cls.raw_maps_table[k]
        cls.record(raw_map, exception)

    @classmethod
    def record(cls, k, exception):
        k = ensure_utf8(k)
        if k not in cls.error_table:
            cls.error_table[k] = exception

    @classmethod
    def get_all_records(cls):
        return cls.error_table.items()
