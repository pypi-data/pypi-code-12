# coding: utf-8
from m3_ext.ui.containers import ExtPanel, ExtContainer as Cnt
from m3_ext.ui.containers.containers import ExtToolBar, ExtToolbarMenu
from m3_ext.ui.containers.context_menu import ExtContextMenu, ExtContextMenuItem
from m3_ext.ui.controls import ExtButton
from m3_ext.ui.icons import Icons
from m3_ext.ui.panels import ExtObjectGrid
from m3_ext.ui.windows import ExtEditWindow, ExtWindow

__author__ = 'damirazo <me@damirazo.ru>'


class DesignerIframeWindow(ExtEditWindow):
    u"""
    Окно с фреймом дизайнера
    """

    def __init__(self, frame_url, report_id):
        super(DesignerIframeWindow, self).__init__()

        self.title = u'Дизайнер отчетов'
        self.maximized = True
        self.closable = False
        self.modal = True
        self.template_globals = 'scripts/DesignerIframeWindow.js'

        self.report_id = report_id

        panel = ExtPanel()
        panel.html = (
            u'<iframe id="creadoc-iframe" src="{}" width="99%" height="99%">'
            u'Фреймы не поддерживаются'
            u'</iframe>'
        ).format(frame_url)

        self.layout = 'border'
        panel.region = 'center'
        panel.layout = 'fit'
        self.items.append(panel)

        # Кнопка закратия окна с подтверждением потери изменений
        self.btn_close = ExtButton()
        self.btn_close.handler = 'closeWindow'
        self.btn_close.style = {'float': 'right', 'margin': '4px 10px 0 0'}
        self.btn_close.text = u'Закрыть окно'

        # Кнопка сохранения текущего состояния шаблона без закрытия окна
        self.btn_save = ExtButton()
        self.btn_save.handler = 'saveTemplate'
        self.btn_save.style = {'float': 'right', 'margin': '4px 10px 0 0'}
        self.btn_save.text = u'Сохранить'

        # Кнопка сохранения шаблона с изменением его имени
        self.btn_save_as = ExtButton()
        self.btn_save_as.handler = 'saveTemplateAs'
        self.btn_save_as.style = {'float': 'right', 'margin': '4px 10px 0 0'}
        self.btn_save_as.text = u'Скопировать'

        self.btn_data_sources = ExtButton()
        self.btn_data_sources.handler = 'openDataSourceWindow'
        self.btn_data_sources.style = {
            'float': 'left',
            'margin': '4px 0 0 10px',
        }
        self.btn_data_sources.text = u'Источники данных'

        self.bottom_bar = Cnt()
        self.bottom_bar.height = 30
        self.bottom_bar.items.extend([
            self.btn_data_sources,
            self.btn_close,
            self.btn_save,
            self.btn_save_as,
        ])


class DesignerReportsListWindow(ExtWindow):
    u"""
    Окно со списком печатных форм
    """

    columns = (
        {
            'header': 'id',
            'data_index': 'id',
            'hidden': True,
        },
        {
            'header': u'Идентификатор',
            'data_index': 'guid',
            'hidden': True,
        },
        {
            'header': u'Наименование',
            'data_index': 'name',
            'sortable': True,
        },
        {
            'header': u'Дата создания',
            'data_index': 'created_at',
            'sortable': True,
        }
    )

    def __init__(self):
        super(DesignerReportsListWindow, self).__init__()

        self.title = u'Список печатных форм'
        self.width = 800
        self.height = 500
        self.layout = 'border'
        self.maximizable = True
        self.minimizable = True
        self.template_globals = 'scripts/DesignerReportsListWindow.js'

        self.grid = self.create_grid()

        menu = ExtContextMenu()
        menu.items.extend([
            ExtContextMenuItem(
                text=u'Импорт шаблона',
                icon_cls='doc-print',
                handler='Ext.emptyFn'
            ),
            ExtContextMenuItem(
                text=u'Экспорт шаблона',
                icon_cls='doc-print',
                handler='exportTemplate'
            ),
        ])

        button_report = ExtToolbarMenu(
            icon_cls='icon-database',
            menu=menu,
            text=u'Функции',
        )

        self.grid.top_bar.items.append(button_report)

        self.items.append(self.grid)

    def create_grid(self):
        grid = ExtObjectGrid()

        for column in self.columns:
            grid.add_column(**column)

        grid.force_fit = True
        grid.layout = 'fit'
        grid.region = 'center'
        grid.allow_paging = False

        return grid


class DesignerDataSourcesWindow(ExtEditWindow):
    u"""
    Окно выбора и подключения источников данных
    """

    columns = (
        {
            'header': u'Идентификатор',
            'data_index': 'id',
            'hidden': True,
        },
        {
            'header': u'Имя переменной в шаблоне',
            'data_index': 'alias',
            'sortable': True,
        },
        {
            'header': u'Описание переменной',
            'data_index': 'name',
            'sortable': True,
        },
        {
            'header': u'Путь',
            'data_index': 'url',
            'sortable': True,
            'hidden': True,
        }
    )

    def __init__(self):
        super(DesignerDataSourcesWindow, self).__init__()

        self.title = u'Список источников данных'
        self.width = 800
        self.height = 500
        self.modal = True
        self.template_globals = 'scripts/DesignerDataSourcesWindow.js'

        self.layout = 'border'

        self.source_grid = self.create_grid('source')
        self.source_grid.region = 'west'
        self.source_grid.width = 390
        self.source_grid.split = True

        self.destination_grid = self.create_grid('destination')
        self.destination_grid.region = 'center'

        self.items.extend([
            self.source_grid,
            self.destination_grid,
        ])

        self.button_add = ExtButton()
        self.button_add.text = u'Подключить'
        self.button_add.icon_cls = Icons.M3_ADD
        self.button_add.handler = 'plugSource'

        self.button_remove = ExtButton()
        self.button_remove.text = u'Отключить'
        self.button_remove.icon_cls = Icons.M3_DELETE
        self.button_remove.handler = 'unplugSource'

        self.top_bar = ExtToolBar()
        self.top_bar.items.extend([
            self.button_add,
            ExtToolBar.Fill(),
            self.button_remove,
        ])

        self.button_submit = ExtButton()
        self.button_submit.text = u'Сохранить'
        self.button_submit.width = 80
        self.button_submit.style = {'float': 'right', 'margin': '4px 10px 0 0'}
        self.button_submit.handler = 'saveSources'

        self.button_cancel = ExtButton()
        self.button_cancel.text = u'Отмена'
        self.button_cancel.width = 80
        self.button_cancel.style = {'float': 'right', 'margin': '4px 10px 0 0'}
        self.button_cancel.handler = 'closeWindow'

        self.bottom_bar = Cnt()
        self.bottom_bar.height = 20

        self.footer_bar = Cnt()
        self.footer_bar.height = 30

        self.footer_bar.items.extend([
            self.button_cancel,
            self.button_submit,
        ])

    def create_grid(self, name):
        grid = ExtObjectGrid()
        grid.name = name
        grid.allow_paging = False
        grid.store.auto_load = False

        for column in self.columns:
            grid.add_column(**column)

        return grid
