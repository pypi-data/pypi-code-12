# coding: utf-8
from operator import attrgetter
from creadoc.models import CreadocReportDataSource
from creadoc.report.exceptions import (
    DuplicateVariableException, DuplicateDataSourceException)

__author__ = 'damirazo <me@damirazo.ru>'


class CreadocRegistry(object):
    u"""
    Реестр шаблонных данных
    Используется для подвязывания и хранения ссылок на шаблонные переменные
    и источники данных
    """

    # Список зарегистрированных переменных
    __variables = []
    # Список зарегистрированных источников данных
    __sources = []
    # Список зарегистрированных псевдонимов источников данных
    __source_aliases = {}
    # Список зарегистрированных уникальных идентификаторов источников данных
    __source_guids = {}

    @classmethod
    def add_variables(cls, *variables):
        u"""
        Регистрация шаблонных переменных
        :param VariableDataSource variables: Одна или несколько
            шаблонных переменных
        :raise: DuplicateVariableException
        """
        existed_names = set(map(attrgetter('name'), cls.__variables))
        added_names = set(map(attrgetter('name'), variables))

        crossed_names = existed_names & added_names

        # Проверка на наличие возможного пересечения в именах переменных
        if crossed_names:
            raise DuplicateVariableException((
                u'Выявлено одно или несколько переменных '
                u'с одинаковыми именами: {}'
            ).format(u', '.join(crossed_names)))

        cls.__variables.extend(variables)

    @classmethod
    def variables(cls):
        u"""
        Перечисление всех зарегистрированных переменных
        :rtype: list
        """
        return cls.__variables

    @classmethod
    def add_sources(cls, *sources):
        u"""
        Регистрация источников данных в реестре
        :param sources: Перечисление источников данных
        :raise: DuplicateDataSourceException
        """
        for source in sources:
            data_source = source()
            alias = data_source.alias
            guid = data_source.guid

            # Проверим, что такое имя переменной еще не использовалось
            if alias in cls.__source_aliases:
                raise DuplicateDataSourceException((
                    u'Источник данных с именем "{}" '
                    u'уже зарегистрирован в реестре в источнике данных "{}"'
                ).format(
                    alias,
                    cls.__source_aliases[alias].__class__.__name__,
                ))

            # Проверим, что данный идентификатор еще не использовался
            if guid in cls.__source_guids:
                raise DuplicateDataSourceException((
                    u'Идентификатор "{}" '
                    u'уже использован в источнике данных "{}"'
                ).format(
                    guid,
                    cls.__source_guids[guid].__class__.__name__,
                ))

            cls.__sources.append(data_source)
            cls.__source_aliases[alias] = data_source
            cls.__source_guids[guid] = data_source

    @classmethod
    def sources(cls):
        u"""
        Перечисление всех зарегистрированных источников данных
        :rtype: list

        """
        return cls.__sources

    @classmethod
    def connected_sources(cls, report_id):
        u"""
        Список всех подключенных к шаблону с указанным id источников данных
        Для нового шаблона список будет пустым
        :param report_id: Идентификатор шаблона
        :rtype: list
        """
        result = []
        # Собираем только подключенные к шаблону источники
        connected_source_ids = CreadocReportDataSource.objects.filter(
            report__id=report_id
        ).values_list('source_uid', flat=True)

        for source in cls.__sources:
            if source.guid in connected_source_ids:
                result.append(source)

        return result

    @classmethod
    def source(cls, guid):
        u"""
        Подключенный источник данных с указанным идентификатором

        :param guid: Идентификатор источника данных
        :type guid: str

        :return: Источник данных или None
        :rtype: creadoc.report.source.DataSource or None
        """
        return cls.__source_guids.get(guid)


# Псевдоним для реестра
CR = CreadocRegistry
