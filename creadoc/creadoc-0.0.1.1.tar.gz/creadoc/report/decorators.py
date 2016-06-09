# coding: utf-8
from m3.actions import PreJsonResult


def data_source(alias, guid, name):
    u"""
    Обертка над экшном. Приводит к формате,
    позволяющему использовать данный экшн в качестве источника данных.

    :param alias: Псевдоним источника данных,
        который будет использовать в качестве имени переменной
    :param guid: Уникальный идентификатор источника данных
    :param name: Наименование источника,
        под которым он будет отображаться в общем списке источников данных
    :rtype: Action
    """

    def _run_wrapper(fn):
        def _inner(self, *args, **kwargs):
            result = fn(self, *args, **kwargs)

            return PreJsonResult({alias: result})
        return _inner

    def wrapper(cls):
        cls.url = '/' + guid
        cls.run = _run_wrapper(cls.run)

        cls.alias = alias
        cls.guid = guid
        cls.name = name

        return cls

    return wrapper
