import os
import time
from pyqode.core.share import Definition
from hackedit.api.plugins import SymbolParserPlugin
from hackedit.app.tasks import SubprocessTaskHandle
from hackedit.app.index import backend, db

DB_PATH = db.DbHelper.get_db_path()
PATH = os.path.join(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'data')), 'FooBarProj')
NEW_FILE = os.path.join(PATH, "spam_eggs.py")
RENAMED_FILE = os.path.join(PATH, "spam.py")
SETUP_PY = os.path.join(PATH, "setup.py")


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    try:
        os.remove(RENAMED_FILE)
    except OSError:
        pass
    try:
        os.remove(NEW_FILE)
    except OSError:
        pass


class FakeParserPlugin(SymbolParserPlugin):
    mimetypes = ['text/x-python']

    def parse(self, path):
        return [Definition('spam', 1, 15, icon=("", ""))]


def remove_db():
    try:
        os.remove(DB_PATH)
    except OSError:
        pass
    assert not os.path.exists(DB_PATH)


def test_index_project_files_no_plugins():
    remove_db()
    time.sleep(1)
    with db.DbHelper():
        pass
    th = SubprocessTaskHandle()
    backend.index_project_files(th, [PATH], [], [])
    with db.DbHelper() as dbh:
        assert len(list(dbh.get_files())) == 3
        assert len(list(dbh.get_symbols())) == 0


def test_index_project_files_with_plugins():
    remove_db()
    time.sleep(1)
    with db.DbHelper():
        pass
    th = SubprocessTaskHandle()
    backend.index_project_files(th, [PATH], [], [FakeParserPlugin()])
    with db.DbHelper() as dbh:
        for row in dbh.get_files():
            print(row[db.COL_FILE_PATH])
        assert len(list(dbh.get_files())) == 3
        assert len(list(dbh.get_symbols())) == 3


def test_update_file():
    remove_db()
    time.sleep(1)
    with db.DbHelper():
        pass
    th = SubprocessTaskHandle()
    backend.index_project_files(th, [PATH], [], [FakeParserPlugin()])

    with db.DbHelper() as dbh:
        fid = dbh.get_file_by_path(SETUP_PY)
    backend.update_file(th, SETUP_PY, fid, PATH, 1,
                        [FakeParserPlugin()])
    # update file time stamp
    with open(SETUP_PY, 'r') as fin:
        with open(SETUP_PY, 'w') as fout:
            fout.write(fin.read())
    backend.update_file(th, SETUP_PY, fid, PATH, 1,
                        [FakeParserPlugin()])


def test_rename_files():
    remove_db()
    time.sleep(1)
    with db.DbHelper():
        pass
    # create a new temporary file that will get renamed
    with open(NEW_FILE, 'w'):
        pass
    th = SubprocessTaskHandle()
    backend.index_project_files(th, [PATH], [], [FakeParserPlugin()])
    with db.DbHelper() as dbh:
        assert len(list(dbh.get_files())) == 4
    os.rename(NEW_FILE, RENAMED_FILE)

    backend.rename_files(th, [(NEW_FILE, RENAMED_FILE)])

    with db.DbHelper() as dbh:
        assert len(list(dbh.get_files())) == 4


def test_delete_files():
    remove_db()
    time.sleep(1)
    with db.DbHelper():
        pass
    # create a new temporary file that will get renamed
    with open(NEW_FILE, 'w'):
        pass
    th = SubprocessTaskHandle()
    backend.index_project_files(th, [PATH], [], [FakeParserPlugin()])
    with db.DbHelper() as dbh:
        nb_files = len(list(dbh.get_files()))
    os.remove(NEW_FILE)

    backend.delete_files(th, [NEW_FILE])

    with db.DbHelper() as dbh:
        assert len(list(dbh.get_files())) == nb_files - 1


def test_cleanup():
    remove_db()
    time.sleep(1)
    with db.DbHelper():
        pass
    # create a new temporary file that will get renamed
    with open(NEW_FILE, 'w'):
        pass
    th = SubprocessTaskHandle()
    backend.index_project_files(th, [PATH], [], [FakeParserPlugin()])
    with db.DbHelper() as dbh:
        nb_files = len(list(dbh.get_files()))
    os.remove(NEW_FILE)

    # reindexing should remove the deleted file
    backend.index_project_files(th, [PATH], [], [FakeParserPlugin()])
    with db.DbHelper() as dbh:
        assert len(list(dbh.get_files())) == nb_files - 1
