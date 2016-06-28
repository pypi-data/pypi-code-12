import os
import shutil

from PyQt5 import QtTest

import pytest_hackedit
from hackedit.api import project
from hackedit.app import settings

PATH1 = os.path.join(os.getcwd(), 'tests', 'data', 'SpamEggsProj2')
PATH2 = os.path.join(os.getcwd(), 'tests', 'data', 'SpamEggsProj3')


def test_open_proj_current_window():
    with pytest_hackedit.MainWindow(PATH1, remove_project_folder=True) as w:
        settings.set_open_mode(settings.OpenMode.CURRENT_WINDOW)
        assert settings.open_mode() == settings.OpenMode.CURRENT_WINDOW
        assert len(project.get_projects()) == 1
        project.open_project(PATH2, sender=w.instance)
        assert len(project.get_projects()) == 2
        QtTest.QTest.qWait(1000)


def test_add_project():
    with pytest_hackedit.MainWindow(PATH1, remove_project_folder=True):
        assert len(project.get_projects()) == 1
        project.add_project(PATH2)
        assert len(project.get_projects()) == 2


def test_open_proj_new_window():
    with pytest_hackedit.MainWindow(PATH1, remove_project_folder=True) as w:
        settings.set_open_mode(settings.OpenMode.NEW_WINDOW)
        assert len(project.get_projects()) == 1
        project.open_project(PATH2, sender=w)
        assert len(w.instance.app.editor_windows) == 2
        assert len(project.get_projects()) == 1
        pytest_hackedit.app().editor_windows[-1].close()


def setup():
    try:
        shutil.rmtree(os.path.join(PATH1, project.FOLDER))
    except OSError:
        pass


def test_user_config():
    settings.load()
    data = project.load_user_config(PATH1)
    assert data == {}
    data = {'Foo': 'bar', 'Spam': 4, 'Eggs': [1, 2, 3]}
    project.save_user_config(PATH1, data)
    usd = project.load_user_config(PATH1)
    assert data == usd
    usd['Foo'] = 'BAR'
    project.save_user_config(PATH1, usd)
