from PyQt5 import QtTest
from hackedit.api import tasks
from hackedit.app.ipc.utils import echo


import pytest_hackedit
from .test_window import PROJ_PATH

finished = False


def test_task_handle():
    th = tasks.TaskHandle()
    th.report_progress("A message", 50)


def callback(*args):
    global finished
    finished = True


def test_start_no_thread():
    global finished
    with pytest_hackedit.MainWindow(PROJ_PATH):
        finished = False
        t = tasks.start('Sample task', echo, callback=callback,
                        use_thread=False)
        assert t is not None
        while not finished:
            QtTest.QTest.qWait(100)


def test_start_with_thread():
    global finished
    with pytest_hackedit.MainWindow(PROJ_PATH):
        finished = False
        t = tasks.start('Sample task', echo, callback=callback,
                        use_thread=True, args=('Spam', 'Eggs'))
        assert t is not None
        while not finished:
            QtTest.QTest.qWait(100)
