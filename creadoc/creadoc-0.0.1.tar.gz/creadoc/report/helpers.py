# coding: utf-8
from creadoc.report.constants import BASE_CATEGORY
from creadoc.report.variable import Variable
from creadoc.report.enums import ValueType

__author__ = 'damirazo <me@damirazo.ru>'


def variable_creator(name, value, category=None, description=None, v_type=None):
    u"""
    Формирование переменной, возвращающего один объект
    :param name: Наименование источника данных
    :param value: Значение, возвращаемое источником данных
    :param category: Наименование категории
    :param description: Описание переменной
    :param v_type: Тип переменной
    :rtype: Variable
    """
    variable = Variable(
        name=name,
        category=category or BASE_CATEGORY,
        description=description or u'',
        v_type=v_type or ValueType.STRING,
    )

    if callable(value):
        variable.value = value
    else:
        variable.value = lambda: value

    return variable
