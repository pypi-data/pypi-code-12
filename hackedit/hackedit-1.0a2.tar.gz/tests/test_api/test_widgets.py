import os
import sys
import time

import pytest
from PyQt5 import QtCore, QtGui, QtTest
from pyqode.core.widgets import OutputWindow

from hackedit.api import widgets


class MyPreferencePage(widgets.PreferencePage):
    def __init__(self):
        super().__init__('My name', QtGui.QIcon.fromTheme('on-s-en-fout'),
                         'Editor')


def test_preference_page(qtbot):
    p = MyPreferencePage()
    qtbot.addWidget(MyPreferencePage())
    assert p.name == 'My name'
    assert p.category == 'Editor'


def test_diff_viewer(qtbot):
    editor = widgets.DiffViewer()
    editor.setPlainText('''
    --- /path/to/original    ''timestamp''
+++ /path/to/new    ''timestamp''
@@ -1,3 +1,9 @@
+This is an important
+notice! It should
+therefore be located at
+the beginning of this
+document!
+
 This part of the
 document has stayed the
 same from version to
@@ -5,16 +11,10 @@
 be shown if it doesn't
 change.  Otherwise, that
 would not be helping to
-compress the size of the
-changes.
-
-This paragraph contains
-text that is outdated.
-It will be deleted in the
-near future.
+compress anything.

 It is important to spell
-check this dokument. On
+check this document. On
 the other hand, a
 misspelled word isn't
 the end of the world.
@@ -22,3 +22,7 @@
 this paragraph needs to
 be changed. Things can
 be added after it.
+
+This paragraph contains
+important new additions
+to this document.''')


def test_find_results_widgets(qtbot):
    widget = widgets.FindResultsWidget()
    qtbot.addWidget(widget)
    widget.hide()
    widget.show_results([('foo.py', [
        (10, 'Some random text', [(0, 1), (1, 2)]),
        (11, 'Some random text', [(4, 5)])])], 'search term')
    assert len(widget.data_list) == 3
    widget.select_first_result()


def test_find_results_widgets_no_occurrences(qtbot):
    widget = widgets.FindResultsWidget()
    qtbot.addWidget(widget)
    widget.hide()
    widget.show_results([], 'search_term')
    widget.show_results([('foo', [])], 'search_term')


def test_find_results_widgets_limit(qtbot):
    widget = widgets.FindResultsWidget()
    qtbot.addWidget(widget)
    widget.hide()
    widget.show_results([], 'search_term')
    widget.show_results([('foo.py', [
        (10, 'Some random text', [(0, 1)])] * 1001)], 'search_term')


class TestRunWidget:

    def test_run_program(self, qtbot):
        w = self.get_widget(qtbot)
        assert w.ui.tabWidget.count() == 0
        tab = w.run_program(sys.executable, ['-m', 'pip', '-V'])
        assert isinstance(tab, OutputWindow)
        assert w.ui.tabWidget.count() == 1
        tab.process.waitForFinished()
        w.apply_preferences()  # for coverage
        assert w.ui.tabWidget.count() == 1

    def test_clear(self, qtbot):
        w = self.get_widget(qtbot)
        t = w.run_program(sys.executable, ['-m', 'pip', '-V'])
        QtTest.QTest.qWait(500)
        assert t.toPlainText()
        qtbot.mouseClick(w.ui.bt_clear, QtCore.Qt.LeftButton)
        assert not t.toPlainText()
        t.process.waitForFinished()

    def test_request_close(self, qtbot):
        w = self.get_widget(qtbot)
        t = w.run_program(sys.executable, ['-m', 'pip', '-V'])
        QtTest.QTest.qWait(10)
        w.close()
        w._on_tab_close_requested(0)
        t.process.waitForFinished()

    def test_reuse_tabs(self, qtbot):
        w = self.get_widget(qtbot)
        t1 = w.run_program(sys.executable, ['-m', 'pip', '-V'])
        t1.process.waitForFinished()
        t = w.run_program(sys.executable, ['-m', 'pip', '-V'])
        assert w.ui.tabWidget.count() == 1
        t.process.waitForFinished()

    def test_run_stop(self, qtbot):
        w = self.get_widget(qtbot)
        t = w.run_program(sys.executable, ['-m', 'pip', 'list'])
        QtTest.QTest.qWait(10)
        assert t.is_running
        qtbot.mouseClick(w.ui.bt_run, QtCore.Qt.LeftButton)
        assert not t.is_running
        qtbot.mouseClick(w.ui.bt_run, QtCore.Qt.LeftButton)
        assert t.is_running
        t.process.waitForFinished()

    def test_pin(self, qtbot):
        w = self.get_widget(qtbot)
        t1 = w.run_program(sys.executable, ['-m', 'pip', '-V'])
        t1.process.waitForFinished()
        qtbot.mouseClick(w.ui.bt_pin, QtCore.Qt.LeftButton)
        t2 = w.run_program(sys.executable, ['-m', 'pip', 'list'])
        assert w.ui.tabWidget.count() == 2
        t1.process.waitForFinished()
        t2.process.waitForFinished()

    def get_widget(self, qtbot):
        w = widgets.RunWidget()
        w._interactive = False
        qtbot.addWidget(w)
        return w


class TestDlgProgress:
    @pytest.mark.parametrize('value', [-1, 0, 50, 99, 100])
    def test_set_progress(self, qtbot, value):
        dlg = widgets.DlgProgress()
        dlg.set_progress(value)

    def test_set_msg(self, qtbot):
        dlg = widgets.DlgProgress()
        dlg.set_message('a message...')


class TestFileIconProvider:
    def test_load_plugins(self):
        widgets.FileIconProvider.load_plugins()

    @pytest.mark.parametrize('path', [__file__, 'invalid_mime.wtf',
                                      os.path.dirname(__file__)])
    def test_icon(self, path):
        ret_val = widgets.FileIconProvider().icon(QtCore.QFileInfo(path))
        assert isinstance(ret_val, QtGui.QIcon)

    @pytest.mark.parametrize('icon_type', [widgets.FileIconProvider.File,
                                           widgets.FileIconProvider.Folder,
                                           widgets.FileIconProvider.Trashcan])
    def test_icon_from_type(self, icon_type):
        ret_val = widgets.FileIconProvider().icon(icon_type)
        assert isinstance(ret_val, QtGui.QIcon)

    def test_mimetype_not_found(self):
        ret_val = widgets.FileIconProvider().icon('file.cbl')
        assert isinstance(ret_val, QtGui.QIcon)

    def test_mimetype_not_found_no_fallback(self):
        ret_val = widgets.FileIconProvider().icon('file.cbl')
        assert isinstance(ret_val, QtGui.QIcon)


class TestDlgRunProcess:
    def test_run_process(self):
        widgets.DlgRunProcess.run_process(
            None, sys.executable, ['-m', 'pip', '-V'], autoclose=True)
        QtTest.QTest.qWait(1000)

    def test_cancel(self):
        dlg = widgets.DlgRunProcess()
        dlg.ui.console.start_process(sys.executable, ['-m', 'pip', '-V'])
        time.sleep(0.001)
        dlg.cancel()
