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

import os.path
import logging
from PyQt5 import Qt, QtCore
from lamiview import utils
from lamiview.dialog_about import QLamiViewAboutDialog


_logger = logging.getLogger(__name__)


class QLamiViewMainWindow(Qt.QMainWindow, utils.QtUiLoad):
    _UI_NAME = 'main_window'

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._setup_dialogs()
        self._setup_actions()
        self._setup_signals()

    def _setup_dialogs(self):
        self._about_dialog = QLamiViewAboutDialog()

    def _setup_ui(self):
        self._load_ui()
        self._setup_scroll_widgets()
        self._combo_command.setFocus()

    def _create_scroll_layout(self, widget):
        cur_layout = widget.layout()

        if cur_layout:
            cur_layout.setParent(None)

        layout = Qt.QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setAlignment(QtCore.Qt.AlignTop)

        return layout

    def _setup_scroll_widgets(self):
        self._scroll_metadata_widget = Qt.QWidget()
        self._scroll_metadata_layout = self._create_scroll_layout(self._scroll_metadata_widget)
        self._scroll_metadata.setWidget(self._scroll_metadata_widget)
        self._scroll_analysis_widget = Qt.QWidget()
        self._scroll_analysis_layout = self._create_scroll_layout(self._scroll_analysis_widget)
        self._scroll_analysis.setWidget(self._scroll_analysis_widget)

    def _show_about_dialog(self):
        pos = self.pos()
        pos.setX(pos.x() + 40)
        pos.setY(pos.y() + 40)
        self._about_dialog.show_move(pos)

    def _goto_to_lami_spec(self):
        utils.goto_url('https://github.com/lttng/lttng-analyses/tree/master/doc')

    def _setup_actions(self):
        self._action_about.triggered.connect(self._show_about_dialog)
        self._action_lami_spec.triggered.connect(self._goto_to_lami_spec)

    def _setup_signals(self):
        pass

    def on_action_quit_triggered(self, fn):
        self._action_quit.triggered.connect(fn)

    def on_btn_metadata_clicked(self, fn):
        self._btn_metadata.clicked.connect(fn)

    def on_btn_analysis_clicked(self, fn):
        self._btn_analysis.clicked.connect(fn)

    def add_command(self, cmd):
        self._combo_command.addItem(cmd)

    def set_command(self, cmd):
        self._combo_command.setCurrentText(cmd)

    def set_path(self, path):
        self._edit_path.setText(path)

    def set_begin(self, begin):
        self._edit_begin.setText(begin)

    def set_end(self, end):
        self._edit_end.setText(end)

    def set_limit(self, limit):
        self._edit_limit.setText(limit)

    def set_output_progress(self, output_progress):
        self._check_output_progress.setChecked(output_progress)

    def set_raw_metadata_html(self, html):
        self._web_raw_metadata.setHtml(html)

    def set_raw_analysis_html(self, html):
        self._web_raw_analysis.setHtml(html)

    def _add_widget_to_scroll_layout(self, layout, title, widget, highlight):
        # remove stretch first
        stretch_item = layout.takeAt(layout.count() - 1)

        # title widget
        if isinstance(title, Qt.QWidget):
            title_widget = title
        else:
            title_widget = Qt.QLabel(title)
            title_widget.setTextFormat(QtCore.Qt.PlainText)
            add_css = ''

            if highlight:
                add_css = 'color: #d35400;'

            title_widget.setStyleSheet('QLabel {{ font-size: 8pt; font-weight: bold; {} }}'.format(add_css))

        layout.addWidget(title_widget)

        # widget
        layout.addWidget(widget)

        # spacer
        layout.addSpacing(12)

        # add stretch again
        layout.addItem(stretch_item)

    def add_metadata_widget(self, title, widget, highlight=False):
        self._add_widget_to_scroll_layout(self._scroll_metadata_layout,
                                          title, widget, highlight)


    def add_analysis_widget(self, title, widget, highlight=False):
        self._add_widget_to_scroll_layout(self._scroll_analysis_layout,
                                          title, widget, highlight)

    def _clear_scroll_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)

            if type(item) is Qt.QWidgetItem:
                item.widget().setParent(None)

        layout.addStretch()

    def clear_metadata_widgets(self):
        self._clear_scroll_layout(self._scroll_metadata_layout)

    def clear_analysis_widgets(self):
        self._clear_scroll_layout(self._scroll_analysis_layout)

    def clear_all(self):
        self.clear_metadata_widgets()
        self.clear_analysis_widgets()
        self.set_raw_metadata_html('')
        self.set_raw_analysis_html('')

    def show_status_message(self, msg):
        self._status_bar.showMessage(msg)

    def clear_status_message(self):
        self._status_bar.clearMessage()

    def enable_input_box(self, enable):
        self._gb_input.setEnabled(enable)

    def enable_output_box(self, enable):
        self._gb_output.setEnabled(enable)

    def focus_raw_metadata(self):
        self._tabs_output.setCurrentIndex(0)

    def focus_metadata(self):
        self._tabs_output.setCurrentIndex(1)

    def focus_raw_analysis(self):
        self._tabs_output.setCurrentIndex(2)

    def focus_analysis(self):
        self._tabs_output.setCurrentIndex(3)

    @property
    def command(self):
        return self._combo_command.currentText()

    @property
    def path(self):
        return self._edit_path.text()

    @property
    def begin(self):
        text = self._edit_begin.text()

        if not text:
            return

        return text

    @property
    def end(self):
        text = self._edit_end.text()

        if not text:
            return

        return text

    @property
    def limit(self):
        text = self._edit_limit.text()

        if not text:
            return

        return text

    @property
    def output_progress(self):
        return self._check_output_progress.isChecked()
