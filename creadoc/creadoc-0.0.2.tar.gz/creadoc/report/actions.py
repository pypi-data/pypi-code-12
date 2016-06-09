# coding: utf-8
from m3.actions import (
    ActionPack, Action, ApplicationLogicException, PreJsonResult)
from creadoc.report.registry import CR


class CreadocDataSourceActionPack(ActionPack):
    u"""
    Пак для подвязывания источников данных,
    представляющих из себя обычные экшены
    """
    url = '/data-source'

    def __init__(self):
        super(CreadocDataSourceActionPack, self).__init__()

        self.action_router = CreadocDataSourceRouterAction()

        self.actions.append(self.action_router)


class CreadocDataSourceRouterAction(Action):
    url = '/router'

    def context_declaration(self):
        return {
            'source_guid': {'type': 'str', 'required': True},
        }

    def run(self, request, context):
        data_source = CR.source(context.source_guid)
        if data_source is None:
            raise ApplicationLogicException((
                u'Источник данных с идентификатором {} отсутствует'
            ).format(context.source_guid))

        # TODO: Возможно надо передавать не весь контекст
        result = data_source.data(request, context)

        return PreJsonResult({data_source.alias: result})
