import os

from PyQt5 import QtTest

import pytest
import pytest_hackedit
from hackedit.api import index
from hackedit.app import settings
from hackedit.app.index import db


finished = False  #: flag set by the callback when indexing task has finished.

DB_PATH = db.DbHelper.get_db_path()
PROJ_PATH = os.path.join(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'data')), 'FooBarProj')
FILE_PATH = os.path.join(PROJ_PATH, 'module.py')
INVALID_FILE_PATH = os.path.join(PROJ_PATH, 'setup2.py')


def remove_db():
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass
    assert not os.path.exists(DB_PATH)


def callback(*args):
    global finished
    finished = True


def test_create_database():
    remove_db()
    assert not os.path.exists(DB_PATH)
    assert index.create_database() is True
    assert os.path.exists(DB_PATH)


def test_get_db_path():
    assert index.get_database_path() == DB_PATH


def do_indexing():
    global finished
    finished = False
    settings.set_indexing_enabled(True)
    task = index.perform_indexation([PROJ_PATH], callback=callback)
    assert task is not None
    while not finished:
        QtTest.QTest.qWait(1000)


def test_perform_indexation():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        do_indexing()
        # disable indexing and make sure no task is running.
        settings.set_indexing_enabled(False)
        task = index.perform_indexation([PROJ_PATH], callback=callback)
        assert task is None


def test_get_all_projects():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        do_indexing()
        projects = list(index.get_all_projects())
        assert len(projects)
        proj = projects[0]
        assert proj.path == PROJ_PATH


def test_get_project_ids():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        do_indexing()
        proj = list(index.get_all_projects())[0]
        result = index.get_project_ids([proj.path])
        assert len(result) == 1
        assert result[0] == 1


def test_get_file():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        do_indexing()
        file = index.get_file(FILE_PATH)
        assert file is not None
        assert file.path == FILE_PATH
        assert file.project_id == 1
        assert file.id != 0
        file = index.get_file(INVALID_FILE_PATH)
        assert file is None


def test_get_files():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        do_indexing()
        files = list(index.get_files(projects=[PROJ_PATH]))
        assert len(files) > 1
        files = list(index.get_files(name_filter='set', projects=[PROJ_PATH]))
        assert len(files) == 1


def test_get_symbols():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        do_indexing()
        with pytest.raises(ValueError):
            list(index.get_symbols(projects=[PROJ_PATH], file=FILE_PATH))

        symbols = list(index.get_symbols(projects=[PROJ_PATH]))
        assert len(symbols)

        symbols = list(index.get_symbols(file=FILE_PATH))
        assert len(symbols) == 3

        symbols = list(index.get_symbols(name_filter='egg'))
        assert len(symbols) == 2


def test_remove_project():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        assert len(list(index.get_all_projects())) == 0
        do_indexing()
        assert len(list(index.get_all_projects())) == 1
        index.remove_project(PROJ_PATH)
        assert len(list(index.get_all_projects())) == 0


def test_cleardatabase():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        remove_db()
        do_indexing()
        assert os.path.exists(DB_PATH)
        assert len(list(index.get_all_projects())) == 1
        assert index.clear_database() is True
        assert os.path.exists(DB_PATH)
        assert len(list(index.get_all_projects())) == 0
