from .test_window import FILE1, FILE2, PROJ_PATH
from hackedit.api import editor
import pytest_hackedit


def test_open_file():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        assert len(editor.get_all_paths()) == 0
        editor.open_file(FILE1)
        assert len(editor.get_all_paths()) == 1
        editor.open_file(FILE2)
        assert len(editor.get_all_paths()) == 2


def test_get_current_editor():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        assert editor.get_current_editor() is None
        editor.open_file(FILE1)
        assert editor.get_current_editor() is not None


def test_get_current_path():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        assert editor.get_current_path() is None
        editor.open_file(FILE1)
        assert editor.get_current_path() == FILE1


def test_get_all_paths():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        editor.open_file(FILE2)
        assert len(editor.get_all_editors()) == 2
        assert editor.get_all_paths() == [FILE1, FILE2]


def test_save_current_editor():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        editor.save_current_editor()


def test_save_all_editors():
    with pytest_hackedit.MainWindow(PROJ_PATH):
        editor.open_file(FILE1)
        editor.open_file(FILE2)
        editor.save_all_editors()
