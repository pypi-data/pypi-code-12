# coding: utf-8
import json
from urllib import quote
from m3_ext.ui.containers import ExtPanel
from m3_ext.ui.windows import ExtEditWindow


class ViewerIframeWindow(ExtEditWindow):
    u"""
    Окно с фреймом просмотрщика отчетов
    """

    def __init__(self, url, report, params):
        super(ViewerIframeWindow, self).__init__()

        self.title = u'Просмотр отчета "{}"'.format(report.name)
        self.maximizable = self.maximized = True
        self.modal = True

        url = '{}?report_id={}'.format(url, report.id)
        if params:
            url += '&params={}'.format(quote(json.dumps(params)))

        panel = ExtPanel()
        panel.html = (
            u'<iframe id="creadoc-iframe" src="{}" width="99%" height="99%">'
            u'Фреймы не поддерживаются'
            u'</iframe>'
        ).format(url)
        panel.region = 'center'
        panel.layout = 'fit'

        self.layout = 'border'
        self.items.append(panel)
