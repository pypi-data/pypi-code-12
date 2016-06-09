# coding: utf-8
__author__ = 'damirazo <me@damirazo.ru>'


class BaseDataSourceException(Exception):
    u"""
    Базовое исключение при обработке источников данных
    """


class DuplicateVariableException(BaseDataSourceException):
    u"""
    Выявление дубликата переменной
    """


class DuplicateDataSourceException(BaseDataSourceException):
    u"""
    Выявление дубликата источника данных
    """