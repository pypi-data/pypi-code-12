# coding: utf-8
from m3.actions import ActionPack, Action
from m3.actions.results import PreJsonResult
from m3_ext.ui.results import ExtUIScriptResult
from creadoc.viewer.actions import CreadocViewerActionPack
from demo.app.helpers import find_pack
from demo.app.reports.forms import RegistryListWindow

__author__ = 'damirazo <me@damirazo.ru>'


class ReportListActionPack(ActionPack):
    u"""
    Базовый пак для списка отчетов
    """
    url = '/reestr'
    title = title_plural = u'Тестовый реестр записей'

    def __init__(self):
        super(ReportListActionPack, self).__init__()

        self.action_list = ReportListWindowAction()
        self.action_rows = ReportListRowsAction()

        self.actions.extend([
            self.action_list,
            self.action_rows,
        ])

    def get_list_url(self):
        return self.action_list.get_absolute_url()


class ReportListWindowAction(Action):
    u"""
    Окно с тестовым списком записей
    """
    url = '/list'

    def run(self, request, context):
        win = RegistryListWindow()
        win.grid.action_data = self.parent.action_rows

        viewer_pack = find_pack(CreadocViewerActionPack)
        win.viewer_url = viewer_pack.action_show.get_absolute_url()

        return ExtUIScriptResult(win, context)


class ReportListRowsAction(Action):
    u"""
    Формирование тестового списка записей
    """
    url = '/rows'

    def run(self, request, context):
        result = []

        for x in xrange(1, 101):
            result.append({
                'id': x,
                'code': x,
                'name': u'Запись #{}'.format(x),
            })

        return PreJsonResult({'rows': result, 'count': len(result)})
