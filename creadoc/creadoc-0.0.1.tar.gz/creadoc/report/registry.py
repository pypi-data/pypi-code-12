# coding: utf-8
from operator import attrgetter
from m3.actions import ControllerCache
from creadoc.models import CreadocReportDataSource
from creadoc.report.actions import CreadocDataSourceActionPack
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

    __creadoc_data_source_pack = None

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
        pack = cls.__creadoc_data_source_pack
        if pack is None:
            pack = ControllerCache.find_pack(CreadocDataSourceActionPack)
            cls.__creadoc_data_source_pack = pack

        for source in sources:
            action = source()
            alias = action.alias
            guid = action.guid

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

            cls.__sources.append(action)
            cls.__source_aliases[alias] = action
            cls.__source_guids[guid] = action

            # Расширение списка экшенов для базового пака происходит в рантайме
            pack.add_action_in_runtime(action)

    @classmethod
    def sources(cls):
        u"""
        Перечисление всех зарегистрированных источников данных
        :rtype: list

        """
        return cls.__sources

    @classmethod
    def connected_sources(cls, report_id, params=None):
        u"""
        Список всех подключенных к шаблону с указанным id источников данных
        Для нового шаблона список будет пустым
        :param report_id: Идентификатор шаблона
        :param params: Настроечные параметры для источников данных
        :rtype: list
        """

        def _wrap_run(fn):
            u"""
            Обертка над методом run экшена.
            Дополняет контекст настроечными параметрами.
            """
            def _wrapper(request, context, *args, **kwargs):
                context.params = params

                return fn(request, context, *args, **kwargs)
            return _wrapper

        result = []
        # Собираем только подключенные к шаблону источники
        connected_source_ids = CreadocReportDataSource.objects.filter(
            report__id=report_id
        ).values_list('source_uid', flat=True)

        for source in cls.__sources:
            if source.guid in connected_source_ids:
                if params is not None:
                    source.run = _wrap_run(source.run)

                result.append(source)

        return result


# Псевдоним для реестра
CR = CreadocRegistry
