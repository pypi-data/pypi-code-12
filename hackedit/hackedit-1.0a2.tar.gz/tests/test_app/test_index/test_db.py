import os
import pytest
from hackedit.app.index import db


DB_PATH = db.DbHelper.get_db_path()


def remove_db():
    try:
        os.remove(DB_PATH)
    except OSError:
        pass
    assert not os.path.exists(DB_PATH)


def test_create_tables():
    remove_db()
    with db.DbHelper():
        pass
    assert os.path.exists(DB_PATH)
    assert os.path.getsize(DB_PATH) > 0


def test_has_project():
    remove_db()
    with db.DbHelper() as dbh:
        assert not dbh.has_project('/home/colin')
        dbh.create_project('/home/colin')
        assert dbh.has_project('/home/colin')


def test_create_project():
    remove_db()
    with db.DbHelper() as dbh:
        assert dbh.get_project('/home/colin') is None
        assert dbh.create_project('/home/colin') == 1
        assert dbh.create_project('/home/colin') == 1
        assert dbh.create_project('/home/colin2') == 2
        assert len(list(dbh.get_projects())) == 2


def test_delete_project():
    remove_db()
    with db.DbHelper() as dbh:
        # project 1: 2 files, 2 symbols
        pid1 = dbh.create_project('/home/colin')
        fid1 = dbh.create_file('/path1', pid1)
        dbh.create_symbol(
            'setToolTip', 10, 45, 'code-variable', '/path/to/icon.png',
            fid1, pid1)
        fid2 = dbh.create_file('/path2', pid1)
        dbh.create_symbol(
            'setToolTip', 10, 45, 'code-variable', '/path/to/icon.png',
            fid2, pid1)

        # project 2: 2 files, 2 symbols
        pid2 = dbh.create_project('/home/colin2')
        fid3 = dbh.create_file('/path3', pid2)
        dbh.create_symbol(
            'setToolTip', 10, 45, 'code-variable', '/path/to/icon.png',
            fid3, pid2)
        fid4 = dbh.create_file('/path4', pid2)
        dbh.create_symbol(
            'setToolTip', 10, 45, 'code-variable', '/path/to/icon.png',
            fid4, pid2)

        assert len(list(dbh.get_files())) == 4
        assert len(list(dbh.get_symbols())) == 4
        assert dbh.delete_project('/home/colin') is True
        # second attempt to delete project should fail
        assert dbh.delete_project('/home/colin') is False
        assert len(list(dbh.get_files())) == 2
        assert len(list(dbh.get_symbols())) == 2


def test_has_file():
    remove_db()
    with db.DbHelper() as dbh:
        assert not dbh.has_file('/home/file.py')
        pid = dbh.create_project('/home/colin')
        dbh.create_file('/home/file.py', pid)
        assert dbh.has_file('/home/file.py')


def test_create_file():
    remove_db()
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        assert dbh.create_file('/home/file.py', pid) == 1
        assert dbh.create_file('/home/file.py', pid) == 1  # already added
        assert dbh.create_file('/home/file2.py', pid) == 2
        assert dbh.create_file('/home/file3.py', pid) == 3
        assert dbh.get_file_by_id(3)[db.COL_FILE_PATH] == '/home/file3.py'


def test_get_project_files():
    remove_db()
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        pid2 = dbh.create_project('/home/colin2')
        dbh.create_file('/home/file.py', pid)
        dbh.create_file('/home/file.txt', pid)
        dbh.create_file('/home/zut.txt', pid)
        dbh.create_file('/home/set_tool_tip.txt', pid)
        dbh.create_file('/home/set_call_tip.txt', pid)
        dbh.create_file('/home/set_tip.txt', pid)
        dbh.create_file('/home/set_tip2.txt', pid2)
        dbh.create_file('/home/testMyCodeEditor.txt', pid2)
    with db.DbHelper() as dbh:
        assert len(list(dbh.get_files(
            project_ids=[pid], name_filter='file'))) == 2
        assert len(list(dbh.get_files(
            project_ids=[pid], name_filter='zu'))) == 1
        items = list(dbh.get_files(project_ids=[pid], name_filter='set tip'))
        assert len(items) == 3
        assert len(list(dbh.get_files(project_ids=[pid], name_filter=''))) == 6
        # check that using multiple projects works too
        assert len(list(dbh.get_files(
            project_ids=[pid, pid2], name_filter='set Tip'))) == 4
        assert len(list(dbh.get_files(name_filter='set tip'))) == 4
        assert len(list(dbh.get_files(name_filter='g'))) == 0
        assert len(list(dbh.get_files())) == 8
        assert len(list(dbh.get_files(project_ids=[pid, pid2],
                                      name_filter='my'))) == 1
        assert len(list(dbh.get_files(project_ids=[pid, pid2],
                                      name_filter='my editor'))) == 1
        assert len(list(dbh.get_files(project_ids=[pid, pid2],
                                      name_filter='code editor'))) == 1


def test_get_files():
    remove_db()
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        assert len(list(dbh.get_files())) == 0
        dbh.create_file('/home/file.py', pid)
        assert len(list(dbh.get_files())) == 1
        dbh.create_file('/home/file.txt', pid)
        assert len(list(dbh.get_files())) == 2
        pid2 = dbh.create_project('/home/colin2')
        dbh.create_file('/home/other.txt', pid2)
        assert len(list(dbh.get_files())) == 3
        assert len(list(dbh.get_files(project_ids=[pid]))) == 2
        assert len(list(dbh.get_files(project_ids=[pid2]))) == 1


def test_file_timestamp():
    remove_db()
    path = '/home/file.py'
    mtime = 1456088731.7597587
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        with pytest.raises(ValueError):
            dbh.get_file_mtime(path)
        with pytest.raises(ValueError):
            dbh.update_file(path, mtime)
        dbh.create_file(path, pid)
        # no time stamp
        assert dbh.get_file_mtime(path) is None
        dbh.update_file(path, mtime)
        assert dbh.get_file_mtime(path) == mtime


def test_delete_files():
    remove_db()
    path = '/home/file.py'
    with db.DbHelper() as dbh:
        assert dbh.delete_file(path) is False
        pid = dbh.create_project('/home/colin')
        file_id = dbh.create_file(path, pid)
        assert dbh.has_file(path)
        dbh.create_symbol(
            'spam', 10, 45, 'code-variable', '/path/to/icon.png', file_id, pid)
        dbh.create_symbol(
            'eggs', 22, 45, 'code-variable', '/path/to/icon.png', file_id, pid)
        assert len(list(dbh.get_files(project_ids=[file_id]))) == 1
        dbh.delete_file(path)
        assert not dbh.has_file(path)
        assert len(list(dbh.get_files(project_ids=[file_id]))) == 0


def test_add_symbols():
    remove_db()
    path = '/home/file.py'
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        file_id = dbh.create_file(path, pid)
        assert len(list(dbh.get_symbols(file_id=file_id))) == 0
        symbol_id = dbh.create_symbol(
            'spam', 10, 45, 'code-variable', '/path/to/icon.png', file_id, pid)
        assert symbol_id == 1
        symbols = list(dbh.get_symbols(file_id=file_id))
        assert len(symbols) == 1
        assert symbols[0][db.COL_SYMBOL_NAME] == 'spam'
        assert symbols[0][db.COL_SYMBOL_LINE] == 10
        assert symbols[0][db.COL_SYMBOL_COLUMN] == 45
        assert symbols[0][db.COL_SYMBOL_ICON_THEME] == 'code-variable'
        assert symbols[0][db.COL_SYMBOL_ICON_PATH] == '/path/to/icon.png'
        assert symbols[0][db.COL_SYMBOL_PARENT_SYMBOL_ID] == 'null'
        assert symbols[0][db.COL_SYMBOL_FILE_ID] == file_id
        assert symbols[0][db.COL_SYMBOL_ID] == symbol_id


def test_get_symbols():
    remove_db()
    path = '/home/file.py'
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        fid = dbh.create_file(path, pid)
        dbh.create_symbol(
            'set_Tool_Tip', 10, 45, 'code-variable',
            '/path/to/icon.png', fid, pid)
        dbh.create_symbol(
            'set_Call_Tip', 10, 45, 'code-variable',
            '/path/to/icon.png', fid, pid)
        dbh.create_symbol(
            'set_Tip', 10, 45, 'code-variable', '/path/to/icon.png', fid, pid)
        dbh.create_symbol(
            'word', 10, 45, 'code-variable', '/path/to/icon.png', fid, pid)
        symbols = list(dbh.get_symbols(name_filter=''))
        assert len(symbols) == 4
        symbols = list(dbh.get_symbols(name_filter='set Tip'))
        assert len(symbols) == 3
        assert symbols[0][db.COL_SYMBOL_NAME] == 'set_Tip'
        assert symbols[1][db.COL_SYMBOL_NAME] == 'set_Tool_Tip'
        assert symbols[2][db.COL_SYMBOL_NAME] == 'set_Call_Tip'


def test_get_file_symbols():
    remove_db()
    path1 = '/home/file.py'
    path2 = '/home/file2.py'
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        fid1 = dbh.create_file(path1, pid)
        fid2 = dbh.create_file(path2, pid)
        dbh.create_symbol(
            'setToolTip', 10, 45, 'code-variable',
            '/path/to/icon.png', fid1, pid)
        dbh.create_symbol(
            'setCallTip', 10, 45, 'code-variable',
            '/path/to/icon.png', fid1, pid)
        dbh.create_symbol(
            'setTip', 10, 45, 'code-variable', '/path/to/icon.png', fid2, pid)
        dbh.create_symbol(
            'word', 10, 45, 'code-variable', '/path/to/icon.png', fid2, pid)
        dbh.create_symbol(
            'word', 10, 45, 'code-variable', '/path/to/icon.png', fid2, pid)
        assert len(list(dbh.get_symbols())) == 5
        assert len(list(dbh.get_symbols(file_id=fid1))) == 2
        assert len(list(dbh.get_symbols(file_id=fid2))) == 3
        assert len(list(dbh.get_symbols(file_id=fid2, name_filter='wo'))) == 2


def test_get_project_symbols():
    remove_db()
    p1 = '/home/colin'
    p2 = '/home/colin2'
    path1 = '/home/file.py'
    path2 = '/home/file2.py'
    with db.DbHelper() as dbh:
        pid1 = dbh.create_project(p1)
        pid2 = dbh.create_project(p2)
        fid1 = dbh.create_file(path1, pid1)
        fid2 = dbh.create_file(path2, pid2)
        dbh.create_symbol(
            'setToolTip', 10, 45, 'code-variable',
            '/path/to/icon.png', fid1, pid1)
        dbh.create_symbol(
            'setCallTip', 10, 45, 'code-variable',
            '/path/to/icon.png', fid1, pid1)
        dbh.create_symbol(
            'setTip', 10, 45, 'code-variable', '/path/to/icon.png', fid2, pid2)
        dbh.create_symbol(
            'word', 10, 45, 'code-variable', '/path/to/icon.png', fid2, pid2)
        dbh.create_symbol(
            'word', 10, 45, 'code-variable', '/path/to/icon.png', fid2, pid2)
        assert len(list(dbh.get_symbols())) == 5
        assert len(list(dbh.get_symbols(project_ids=[pid1]))) == 2
        assert len(list(dbh.get_symbols(project_ids=[pid2]))) == 3
        assert len(list(dbh.get_symbols(
            project_ids=[pid2], name_filter='wo'))) == 2


def test_delete_file_symbols():
    remove_db()
    path = '/home/file.py'
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        file_id = dbh.create_file(path, pid)
        dbh.create_symbol(
            'spam', 10, 45, 'code-variable', '/path/to/icon.png', file_id, pid)
        dbh.create_symbol(
            'eggs', 22, 45, 'code-variable', '/path/to/icon.png', file_id, pid)
        assert len(list(dbh.get_symbols(file_id=file_id))) == 2
        dbh.delete_file_symbols(file_id)
        assert len(list(dbh.get_symbols(file_id=file_id))) == 0


def test_is_camel_case():
    assert db.DbHelper.is_camel_case('TESTMYCODEEDIT') is False
    assert db.DbHelper.is_camel_case('TestMyCodeEdit') is True
    assert db.DbHelper.is_camel_case('testMyCodeEdit') is True


def test_unescaped_symbol():
    remove_db()
    path = '/home/file.py'
    with db.DbHelper() as dbh:
        pid = dbh.create_project('/home/colin')
        file_id = dbh.create_file(path, pid)
        assert len(list(dbh.get_symbols(file_id=file_id))) == 0
        symbol_id = dbh.create_symbol(
            "78 SOME-VAR VALUE '459'", 10, 45, 'code-variable',
            '/path/to/icon.png', file_id, pid)
        assert symbol_id == 1
        symbols = list(dbh.get_symbols(file_id=file_id))
        assert len(symbols) == 1
        assert symbols[0][db.COL_SYMBOL_NAME] == "78 SOME-VAR VALUE '459'"
