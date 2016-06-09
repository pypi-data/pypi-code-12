# coding: utf-8
from creadoc.report.helpers import variable_creator
from creadoc.report.registry import CR
from creadoc.report.enums import ValueType
from demo.app.example.actions import ReportTestData4Action


# Регистрация источников данных
CR.add_sources(ReportTestData4Action)


# Регистрация шаблонных переменных
CR.add_variables(
    variable_creator(
        'Hello',
        u'Привет, Мир!',
        description=u'Тестовое описание переменной'),
    variable_creator(
        'EnterpriseName',
        u'Касатка',
        category=u'ЗиК',
        description=u'Наименование учреждения'),
    variable_creator(
        'OperationDate',
        '01.01.2012',
        category=u'ЗиК',
        v_type=ValueType.DATETIME,
        description=u'Рабочая дата учреждения'),
)
