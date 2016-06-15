# coding: utf-8
import json
from m3.actions import ControllerCache
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
    variable = Variable()
    variable.name = name
    variable.category = category or BASE_CATEGORY
    variable.description = description or u''
    variable.type = v_type or ValueType.STRING

    if callable(value):
        variable.value = value
    else:
        variable.value = lambda: value

    return variable


def data_source_url(guid, params=None):
    from creadoc.report.actions import CreadocDataSourceActionPack

    router_pack = ControllerCache.find_pack(CreadocDataSourceActionPack)

    if params is not None:
        params_string = '&params={}'.format(json.dumps(params))
    else:
        params_string = ''

    url = '{}?guid={}{}'.format(
        router_pack.action_router.get_absolute_url(),
        guid, params_string)

    return url
