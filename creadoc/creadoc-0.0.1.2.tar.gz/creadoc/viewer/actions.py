# coding: utf-8
from django.http import HttpResponse
from django.template import loader
from django.template.context import Context
from m3 import ApplicationLogicException
from m3.actions import ActionPack, Action
from m3_ext.ui.results import ExtUIScriptResult
from creadoc.models import CreadocReport
from creadoc.report.registry import CR
from creadoc.viewer.forms import ViewerIframeWindow


class CreadocViewerActionPack(ActionPack):
    u"""
    Базовый пак для просмотрщика отчетов
    """
    url = '/viewer'
    title = title_plural = u'Просмотр отчета'

    def __init__(self):
        super(CreadocViewerActionPack, self).__init__()

        self.action_show = CreadocViewerShowAction()
        self.action_iframe = CreadocViewerIframeAction()

        self.actions.extend([
            self.action_show,
            self.action_iframe,
        ])


class CreadocViewerShowAction(Action):
    u"""
    Формирование окна с фреймом просмотрщика
    """
    url = '/show'

    def context_declaration(self):
        return {
            'report_id': {'type': 'int', 'required': True},
            'background_mode': {
                'type': 'boolean',
                'required': True,
                'default': False,
            },
            'params': {'type': 'json', 'required': True, 'default': {}},
        }

    def run(self, request, context):
        try:
            report = CreadocReport.objects.get(pk=context.report_id)
        except CreadocReport.DoesNotExist:
            raise ApplicationLogicException((
                u'Шаблон отчетной формы с id={} отсутствует, '
                u'возможно он был удален.'
            ).format(context.report_id))

        win = ViewerIframeWindow(
            url=self.parent.action_iframe.get_absolute_url(),
            report=report,
            params=context.params)

        return ExtUIScriptResult(win, context)


class CreadocViewerIframeAction(Action):
    u"""
    Формирование фрейма с просмотрщиком
    """
    url = '/iframe'

    def context_declaration(self):
        return {
            'report_id': {'type': 'int', 'required': True},
            'params': {'type': 'json', 'required': True, 'default': {}},
        }

    def run(self, request, context):
        try:
            report = CreadocReport.objects.get(pk=context.report_id)
        except CreadocReport.DoesNotExist:
            raise ApplicationLogicException((
                u'Шаблон отчетной формы с id={} отсутствует, '
                u'возможно он был удален.'
            ).format(context.report_id))

        template_url = report.url

        t = loader.get_template('viewer.html')

        ctx = Context()
        ctx['template_url'] = template_url
        # Перечисление шаблонных переменных
        ctx['variables'] = CR.variables()
        # Перечисление подключенных источников данных
        ctx['sources'] = CR.connected_sources(context.report_id)

        return HttpResponse(t.render(ctx))
