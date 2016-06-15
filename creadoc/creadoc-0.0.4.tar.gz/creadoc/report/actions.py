# coding: utf-8
from m3.actions import (
    ActionPack, Action, ApplicationLogicException, PreJsonResult)
from creadoc.report.registry import CR


class CreadocDataSourceActionPack(ActionPack):
    u"""
    Пак для работы с источниками данных
    """
    url = '/data-source'

    def __init__(self):
        super(CreadocDataSourceActionPack, self).__init__()

        self.action_router = CreadocDataSourceRouterAction()

        self.actions.append(self.action_router)


class CreadocDataSourceRouterAction(Action):
    u"""
    Действие-маршрутизатор, управляет загрузкой источников данных
    """
    url = '/router'

    def context_declaration(self):
        return {
            'guid': {'type': 'str', 'required': True},
            'params': {'type': 'json', 'required': True, 'default': {}},
        }

    def run(self, request, context):
        data_source = CR.source(context.guid)
        if data_source is None:
            raise ApplicationLogicException((
                u'Источник данных с идентификатором {} отсутствует'
            ).format(context.source_guid))

        result = data_source.load(context.params)

        return PreJsonResult({data_source.alias: result})
