# coding: utf-8
__author__ = 'damirazo'


class DataSource(object):
    u"""
    Базовый класс для источника данных
    """
    guid = None
    u"""
    Уникальный идентификатор источника данных
    :type: None or str
    """

    name = None
    u"""
    Название источника данных
    :type: None or unicode
    """

    alias = None
    u"""
    Псевдоним источника данных, используется в шаблонах
    :type: None or str
    """

    def load(self, params=None):
        u"""
        Загрузка данных из источника.
        В случае отсутствия данных используется значение по умолчанию.
        """
        if params is None:
            params = {}

        return (
            self.data(params) or self.default_value(params)
        )

    def data(self, params):
        u"""
        Формирование набора данных для заполнения источника
        """
        raise NotImplementedError

    def default_value(self, params):
        u"""
        Значение источника данных по умолчанию.
        Используется в случае отсутствия данных.
        """
        raise NotImplementedError


def required_params(*fields):
    def inner(method):
        def outer(self, params, *args, **kwargs):
            for field in fields:
                if field not in params:
                    return self.default_value(params, *args, **kwargs)

            return method(self, params, *args, **kwargs)

        return outer
    return inner
