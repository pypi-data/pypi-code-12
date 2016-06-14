# coding: utf-8

__author__ = 'damirazo <me@damirazo.ru>'


class Variable(object):
    u"""
    Базовый класс для шаблонной переменной

    В каждой шаблонной переменной требуется реализовать метод value,
    возвращающий значение, которое требуется подставить в шаблон.
    Вызов осуществляется единожды при регистрации переменной в CreadocRegistry.
    """
    name = None
    category = None
    description = None
    type = None

    def value(self):
        raise NotImplementedError(u'Требуется реализовать метод value!')
