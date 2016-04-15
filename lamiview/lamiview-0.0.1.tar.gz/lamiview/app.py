# The MIT License (MIT)
#
# Copyright (c) 2016 Philippe Proulx <pproulx@efficios.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from lamiview.dialog_progress import QLamiViewProgressDialog
from lamiview.main_window import QLamiViewMainWindow
from collections import namedtuple
from PyQt5 import Qt, QtCore
import pygments.lexers.data
import pygments.formatters
from lamiview import lami
import pygments
import argparse
import platform
import pygments
import logging
import json
import sys
import os
import re


_logger = logging.getLogger(__name__)


_Config = namedtuple('_Config', ['commands'])


class _QLamiViewApp(Qt.QApplication):
    _UPDATE_TIMER_MS = 1000

    def __init__(self, args):
        super().__init__([sys.argv[0]])
        self._args = args
        self.setOrganizationName('eepp.ca')
        self.setApplicationName('lamiview')
        self._setup()
        self._start()

    def _start(self):
        _logger.info('Starting application')
        self._main_window.show()

    def _setup(self):
        self._load_config()
        self._setup_ui()
        self._setup_quit_timer()
        self._setup_actions()

    def _setup_ui(self):
        self._main_window = QLamiViewMainWindow()
        self._progress_dialog = QLamiViewProgressDialog()
        self._init_input()

    def _init_input(self):
        for command in self._config.commands:
            self._main_window.add_command(command)

        if self._args.cmd:
            self._main_window.set_command(self._args.cmd)

        if self._args.path:
            self._main_window.set_path(self._args.path[0])

        if self._args.begin:
            self._main_window.set_begin(self._args.begin)

        if self._args.end:
            self._main_window.set_end(self._args.end)

        if self._args.limit:
            self._main_window.set_limit(self._args.limit)

        if self._args.output_progress:
            self._main_window.set_output_progress(self._args.output_progress)

    def _show_progress_dialog(self):
        pos = self._main_window.pos()
        pos.setX(pos.x() + 40)
        pos.setY(pos.y() + 40)
        self._progress_dialog.reset()
        self._progress_dialog.set_value(.45)
        self._progress_dialog.set_message('29312 events processed')
        self._progress_dialog.show_move(pos)

    def _setup_actions(self):
        self._main_window.on_action_quit_triggered(self.closeAllWindows)
        self._main_window.on_btn_metadata_clicked(self._get_metadata)
        self._main_window.on_btn_analysis_clicked(self._get_analysis)

    def _setup_quit_timer(self):
        self._quit_timer = Qt.QTimer()
        self._quit_timer.timeout.connect(lambda: None)
        self._quit_timer.start(250)

    def _load_config(self):
        self._config = _Config(commands=[])
        config_path = os.getenv('LAMIVIEW_CONFIG_PATH',
                                os.path.expanduser('~/.config/lamiview/config.json'))

        if not os.path.isfile(config_path):
            _logger.warning('Config file "{}" is not an existing file'.format(config_path))
            return

        try:
            with open(config_path, 'r') as f:
                json_config = json.load(f)
        except Exception as e:
            _logger.warning('Cannot open/parse config file "{}": {}'.format(config_path, e))
            return

        _logger.info('Loaded config file "{}"'.format(config_path))
        commands = []

        if 'commands' in json_config and type(json_config['commands']) is list:
            for command in json_config['commands']:
                if type(command) is str:
                    _logger.info('Adding command "{}" from config file'.format(command))
                    commands.append(command)
                else:
                    _logger.warning('Not adding invalid command "{}" from config file'.format(command))

        self._config = _Config(commands=commands)

    def _show_status_message(self, msg):
        self._main_window.show_status_message(msg)

    def _clear_status_message(self):
        self._main_window.clear_status_message()

    def _dict_to_json_html(self, dictionary):
        json_str = json.dumps(dictionary, indent=2, sort_keys=True)
        formatter = pygments.formatters.HtmlFormatter(noclasses=True,
                                                      nobackground=True)
        lexer = pygments.lexers.data.JsonLexer()
        json_html = pygments.highlight(json_str, lexer, formatter)
        html = '''
            <!doctype html>
            <html>
              <head>
                <meta charset="utf-8">
                <title></title>
                <style type="text/css">
                  html {{
                    font-size: 8pt;
                  }}

                  body, div, pre {{
                    margin: 0;
                    padding: 0;
                  }}

                  pre {{
                    padding: 1em;
                  }}
                </style>
              </head>
              <body>{}</body>
            </html>'''.format(json_html)

        return html

    def _create_base_table_widget(self):
        table = Qt.QTableWidget()
        table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        table.setStyleSheet('''
            QWidget {
              font-size: 7pt;
              font-family: monospace;
            }

            QHeaderView {
              font-weight: bold;
              font-family: sans-serif;
            }''')

        return table

    def _create_table_widget_item(self, text):
        item = Qt.QTableWidgetItem(text)
        item.setFlags(QtCore.Qt.NoItemFlags | QtCore.Qt.ItemIsEnabled)

        return item

    def _fix_table_widget(self, table):
        table.verticalHeader().setDefaultSectionSize(15)
        table.resizeColumnsToContents()
        hheader = table.horizontalHeader()

        for index in range(hheader.count()):
            section_size = hheader.sectionSize(index)
            section_size += 6
            hheader.resizeSection(index, section_size)

        height = (table.rowCount()) * 15 + table.horizontalHeader().height() + 1
        height += table.horizontalScrollBar().height()
        table.setMaximumHeight(height)
        table.setMinimumHeight(height)

    def _create_metadata_infos_table(self, metadata):
        rows = []
        rows.append(('MI version', str(metadata.mi_version)))

        if metadata.version is not None:
            rows.append(('Version', str(metadata.version)))

        if metadata.title is not None:
            rows.append(('Title', str(metadata.title)))

        if metadata.authors:
            rows.append(('Authors', ', '.join(metadata.authors)))

        if metadata.description is not None:
            rows.append(('Description', metadata.description))

        if metadata.url is not None:
            rows.append(('URL', metadata.url))

        if metadata.tags:
            rows.append(('Tags', ', '.join(metadata.tags)))

        table = self._create_base_table_widget()
        table.setRowCount(len(rows))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(('Property', 'Value'))

        for row_index, row in enumerate(rows):
            prop = self._create_table_widget_item(row[0])
            value = self._create_table_widget_item(row[1])
            table.setItem(row_index, 0, prop)
            table.setItem(row_index, 1, value)

        self._fix_table_widget(table)

        return table

    def _wrap_table_horizontally(self, table):
        return table

    def _create_metadata_table_class_table(self, table_class):
        table = self._create_base_table_widget()
        table.setRowCount(len(table_class.column_descriptions))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(('Title', 'Class', 'Unit'))

        for row_index, cd in enumerate(table_class.column_descriptions):
            title = ''
            cls = 'mixed'
            unit = ''

            if cd.title:
                title = cd.title

            if cd.cls is not None:
                if type(cd.cls) is str:
                    cls = cd.cls
                else:
                    cls = cd.cls.NAME

            if cd.unit:
                unit = cd.unit

            title = self._create_table_widget_item(title)
            cls = self._create_table_widget_item(cls)
            unit = self._create_table_widget_item(unit)
            table.setItem(row_index, 0, title)
            table.setItem(row_index, 1, cls)
            table.setItem(row_index, 2, unit)

        self._fix_table_widget(table)

        return table

    def _set_metadata_output(self, metadata):
        # clear things
        self._main_window.set_raw_metadata_html('')
        self._main_window.clear_metadata_widgets()

        raw_metadata_html = self._dict_to_json_html(metadata.dict)
        self._main_window.set_raw_metadata_html(raw_metadata_html)

        # set interpreted metadata output
        if type(metadata) is lami.Error:
            return

        metadata_table = self._create_metadata_infos_table(metadata)
        widget = self._wrap_table_horizontally(metadata_table)
        self._main_window.add_metadata_widget('Infos', widget)

        for cls_name, table_class in metadata.table_classes.items():
            table = self._create_metadata_table_class_table(table_class)
            title = 'Table class <span style="color: #d35400;">{}</span>'.format(cls_name)
            title_widget = Qt.QLabel(title)
            title_widget.setStyleSheet('QLabel { font-size: 8pt; font-weight: bold; }')
            widget = self._wrap_table_horizontally(table)
            self._main_window.add_metadata_widget(title_widget, widget)

    def _get_metadata(self):
        # clear things
        self._main_window.clear_all()

        # get metadata
        self._show_status_message('Getting metadata...')
        self._main_window.enable_input_box(False)
        Qt.QCoreApplication.processEvents()

        try:
            metadata = lami.get_metadata(self._main_window.command)
        except Exception as e:
            self._main_window.set_raw_metadata_html(self._get_html_error(str(e)))
            self._main_window.focus_raw_metadata()
            return
        finally:
            self._clear_status_message()
            self._main_window.enable_input_box(True)

        # set raw metadata output
        self._set_metadata_output(metadata)
        self._main_window.focus_metadata()

    def _create_analysis_result_table(self, result_table):
        table = self._create_base_table_widget()
        table.setRowCount(len(result_table.rows))
        table.setColumnCount(len(result_table.cls.column_descriptions))
        labels = []

        for index, cd in enumerate(result_table.cls.column_descriptions):
            def make_label(parts):
                if unit:
                    parts.append('({})'.format(unit))

                return ' '.join(parts)

            if cd.title:
                title = cd.title
            else:
                title = 'Column #{}'.format(index + 1)

            unit = None

            if cd.unit:
                unit = cd.unit
            else:
                if hasattr(cd.cls, 'UNIT') and cd.cls.UNIT:
                    unit = cd.cls.UNIT

            if cd.cls.COLUMNS:
                for col_name, col_attr in cd.cls.COLUMNS:
                    labels.append(make_label([title, '[{}]'.format(col_name)]))
            else:
                labels.append(make_label([title]))

        table.setHorizontalHeaderLabels(tuple(labels))

        for row_index, row in enumerate(result_table.rows):
            cells = []

            for col_index, cell in enumerate(row):
                cd = result_table.cls.column_descriptions[col_index]

                if cd.cls.COLUMNS:
                    for col_name, col_attr in cd.cls.COLUMNS:
                        if type(cell) is lami.Unknown:
                            cells.append('?')
                        elif type(cell) is lami.Empty:
                            cells.append('')
                        else:
                            attr_value = getattr(cell, col_attr)
                            cells.append(str(attr_value))
                else:
                    cells.append(str(cell))

            for col_index, cell in enumerate(cells):
                item = self._create_table_widget_item(cell)
                table.setItem(row_index, col_index, item)

        self._fix_table_widget(table)

        return table

    def _get_analysis(self):
        def on_progress_update(progress):
            if progress.message:
                self._progress_dialog.set_message(progress.message)

            self._progress_dialog.set_value(progress.value)
            Qt.QCoreApplication.processEvents()

        # clear things
        self._main_window.clear_all()

        # get analysis results
        command = self._main_window.command
        path = self._main_window.path
        begin = self._main_window.begin
        end = self._main_window.end
        limit = self._main_window.limit
        output_progress = self._main_window.output_progress

        if output_progress:
            self._show_progress_dialog()

        self._show_status_message('Getting analysis results...')
        self._main_window.enable_input_box(False)
        Qt.QCoreApplication.processEvents()

        try:
            results = lami.get_analysis_results(command, path, begin, end, limit,
                                                output_progress, on_progress_update)
        except Exception as e:
            self._main_window.set_raw_analysis_html(self._get_html_error(str(e)))
            self._main_window.focus_raw_analysis()
            return
        finally:
            self._clear_status_message()
            self._progress_dialog.done(0)
            self._main_window.enable_input_box(True)

        # set raw analysis results output
        raw_analysis_html = self._dict_to_json_html(results.dict)
        self._main_window.set_raw_analysis_html(raw_analysis_html)

        # set interpreted analysis results output
        if type(results) is lami.Error:
            return

        # set metadata output
        self._set_metadata_output(results.metadata)

        for index, result_table in enumerate(results.result_tables):
            if result_table.cls.title:
                title = result_table.cls.title
            else:
                title = 'Result table #{}'.format(index + 1)

            title_widget = Qt.QLabel(title)
            title_widget.setTextFormat(QtCore.Qt.PlainText)
            title_widget.setStyleSheet('''
                QLabel {
                  color: #d35400;
                  font-size: 8pt;
                  font-weight: bold;
                }''')

            horiz_widget = Qt.QWidget()
            horiz_layout = Qt.QHBoxLayout(horiz_widget)
            horiz_layout.setContentsMargins(0, 0, 0, 0)
            horiz_layout.setSpacing(12)
            horiz_layout.addWidget(title_widget)
            horiz_layout.addStretch()

            if result_table.time_range:
                label = Qt.QLabel(str(result_table.time_range))
                label.setTextFormat(QtCore.Qt.PlainText)
                label.setStyleSheet('''
                    QLabel {
                      font-size: 8pt;
                      font-family: monospace;
                      font-weight: bold;
                    }''')
                horiz_layout.addWidget(label)

            widget = self._create_analysis_result_table(result_table)
            self._main_window.add_analysis_widget(horiz_widget, widget)

        self._main_window.focus_analysis()

    def _get_html_error(self, msg):
        return '''
            <!doctype html>
            <html>
              <head>
                <meta charset="utf-8">
                <title></title>
                <style type="text/css">
                  html {{
                    font-size: 8pt;
                  }}

                  body, div, p {{
                    margin: 0;
                    padding: 0;
                  }}

                  body {{
                    margin: 1em;
                    font-family: monospace;
                  }}

                  p {{
                    color: #c0392b;
                  }}
                </style>
              </head>
              <body>
                <p><strong>Error</strong> while executing the command:<br>{}</p>
              </body>
            </html>'''.format(msg)


def _register_sigint(app):
    if platform.system() == 'Linux':
        def handler(signal, frame):
            _logger.info('Got SIGINT')
            sys.exit(0)

        import signal

        signal.signal(signal.SIGINT, handler)


def _configure_logging():
    fmt = '%(asctime)s [%(levelname)7s] ' \
          '%(message)s (%(funcName)s@%(filename)s:%(lineno)d)'
    logging.basicConfig(level=logging.INFO, format=fmt)


def _parse_args():
    import lamiview

    ap = argparse.ArgumentParser()
    ap.add_argument('-V', '--version', action='version',
                    version='%(prog)s v{}'.format(lamiview.__version__))
    ap.add_argument('-b', '--begin', metavar='TS', action='store',
                    help='beginning timestamp')
    ap.add_argument('-e', '--end', metavar='TS', action='store',
                    help='ending timestamp')
    ap.add_argument('-l', '--limit', metavar='COUNT', action='store',
                    help='maximum rows/table')
    ap.add_argument('-p', '--output-progress', action='store_true',
                    help='show progress indication')
    ap.add_argument('-c', '--cmd', metavar='COMMAND', action='store',
                    help='command')
    ap.add_argument('path', metavar='PATH', action='store', nargs='*',
                    help='trace path')

    # parse args
    args = ap.parse_args()

    if len(args.path) > 1:
        _logger.error('Command-line error: Please specify zero or one trace path')
        return None

    return args


def run():
    args = _parse_args()

    if args is None:
        return 1

    _configure_logging()
    app = _QLamiViewApp(args)
    _register_sigint(app)
    rc = app.exec_()
    _logger.info('App returned exit status {}'.format(rc))

    return rc


if __name__ == '__main__':
    run()
