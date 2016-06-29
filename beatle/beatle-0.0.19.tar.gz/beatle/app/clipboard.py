# -*- coding: utf-8 -*-

# This file defines a ver basic private clipboard
# whose mission is to handle data and provide info about

from deco import classproperty
import uuid


class clipboard(object):
    "Basic clipboard definition"
    # propiedades
    __registered__classes = {}
    __current_data = None

    def __init__(self):
        """Initialization. Setup handlers"""
        super(clipboard, self).__init__()

    @classproperty
    def is_empty(cls):
        """has data?"""
        return not cls.__current_data

    @classmethod
    def register(cls, type):
        """register a new class or access it"""
        if type not in cls.__registered__classes:
            cls.__registered__classes[type] = uuid.uuid4()
        return cls.__registered__classes[type]

    @classmethod
    def copy(cls, data):
        """copy data to clipboard"""
        assert type(data) in cls.__registered__classes
        if id(data) != id(cls.__current_data):
            cls.__current_data = data

    @classproperty
    def info(cls):
        """return clipboard info"""
        return cls.__current_data and cls.__registered__classes[
            type(cls.__current_data)]

    @classproperty
    def data(cls):
        """return the current data"""
        return cls.__current_data

