# coding: utf-8

__author__ = 'damirazo <me@damirazo.ru>'


class Variable(object):
    u"""
    Базовый класс для шаблонной переменной

    В каждой шаблонной переменной требуется реализовать метод value,
    возвращающий значение, которое требуется подставить в шаблон.
    Вызов осуществляется единожды при регистрации переменной в CreadocRegistry.
    """

    def __init__(self, name, category, description, v_type):
        u"""
        :param name: Наименование переменной
        :param category: Категория переменной.
            Переменные с одной категорией группируются в одну "папку"
        :param description: Описание переменной
        :param v_type: Тип переменной. Значение из перечисления ValueType
        """
        self.name = name
        self.category = category
        self.description = description
        self.type = v_type

    def value(self):
        raise NotImplementedError(u'Требуется реализовать метод value!')
