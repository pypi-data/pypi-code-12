"""
Low level api for managing the file/symbols index.
"""
import logging
import os
import sqlite3

import sys

import re

from hackedit.api import system


#: Version of the database (will be appended to the db filename)
DB_VERSION = '0.1'
#: File name of the database
DB_FILE_NAME = 'index-%s.db' % DB_VERSION
if os.environ.get('HACKEDIT_CORE_TEST_SUITE', default=None) is not None:
    DB_FILE_NAME = 'test-index-%s.db' % DB_VERSION

#: sql statements used to create the file and symbol tables.
SQL_CREATE_TABLES = [
    # Project table
    """CREATE TABLE Project (
        PROJECT_ID INTEGER PRIMARY KEY,
        PROJECT_PATH VARCHAR(512),
        PROJECT_NAME VARCHAR(256));
    """,

    # File table
    """CREATE TABLE File (
        FILE_ID INTEGER PRIMARY KEY,
        FILE_PATH VARCHAR(512),
        FILE_TIME_STAMP FLOAT,
        FILE_NAME VARCHAR(256),
        PROJECT_ID INT NOT NULL REFERENCES Project(PROJECT_ID));
    """,

    "CREATE VIRTUAL TABLE File_index USING fts4(FILE_ID INT, CONTENT);",

    # Symbol table
    """CREATE TABLE Symbol (
        SYMBOL_ID INTEGER PRIMARY KEY,
        SYMBOL_LINE INT,
        SYMBOL_COLUMN INT,
        SYMBOL_ICON_THEME VARCHAR(128),
        SYMBOL_ICON_PATH VARCHAR(256),
        SYMBOL_NAME VARCHAR(256),
        FILE_ID INT NOT NULL REFERENCES File(FILE_ID),
        PROJECT_ID INT NOT NULL REFERENCES Project(PROJECT_ID),
        PARENT_SYMBOL_ID INT REFERENCES Symbol(SYMBOL_ID));
    """,

    """CREATE TABLE Todo (
        TODO_ID INTEGER PRIMARY KEY,
        TODO_LINE INT,
        TODO_COLUMN INT,
        TODO_CONTENT VARCHAR(256),
        FILE_ID INT NOT NULL REFERENCES File(FILE_ID),
        PROJECT_ID INT NOT NULL REFERENCES Project(PROJECT_ID));
    """,

    "CREATE VIRTUAL TABLE Symbol_index USING fts4(SYMBOL_ID INT, CONTENT);",
]

#: name of the project id column
COL_PROJECT_ID = 'PROJECT_ID'
#: name of the project path column
COL_PROJECT_PATH = 'PROJECT_PATH'
#: name of the project nale column
COL_PROJECT_NAME = 'PROJECT_NAME'
#: name of the file id column
COL_FILE_ID = 'FILE_ID'
#: name of the file path column
COL_FILE_PATH = 'FILE_PATH'
#: name of the file mtime column
COL_FILE_TIME_STAMP = 'FILE_TIME_STAMP'
#: name of the file mtime column
COL_FILE_NAME = 'FILE_NAME'
#: name of the file project id column
COL_FILE_PROJECT_ID = COL_PROJECT_ID
#: name of the symbol id column
COL_SYMBOL_ID = 'SYMBOL_ID'
#: name of the symbol line column
COL_SYMBOL_LINE = 'SYMBOL_LINE'
#: name of the symbol column column
COL_SYMBOL_COLUMN = 'SYMBOL_COLUMN'
#: name of the symbol icon theme column
COL_SYMBOL_ICON_THEME = 'SYMBOL_ICON_THEME'
#: name of the symbol icon path column
COL_SYMBOL_ICON_PATH = 'SYMBOL_ICON_PATH'
#: name of the symbol name column
COL_SYMBOL_NAME = 'SYMBOL_NAME'
#: name of the symbol file id column
COL_SYMBOL_FILE_ID = COL_FILE_ID
#: name of the symbol parent symbol id column
COL_SYMBOL_PARENT_SYMBOL_ID = 'PARENT_SYMBOL_ID'


class DbHelper:
    """
    Context manager that open a database connection and let you execute some
    actions on it. The connection is automatically closed when the context
    manager goes out of scope.

    .. note:: The database tables are created automatically if the database
        file did not exist.
    """
    prog_camel_case = re.compile(r'(?:[A-Z][a-z]+)+')

    def __init__(self):
        """
        :param db_path: Path to the database file.
        """
        self.conn = None
        self.exists = os.path.exists(self.get_db_path())

    def __enter__(self):
        """
        Enters the context manager: creates the database if it does not exists
        and create the connection object.
        """
        db_path = self.get_db_path()
        self.conn = sqlite3.connect(db_path, timeout=60)
        self.conn.row_factory = sqlite3.Row
        if not self.exists:
            _logger().debug('creating database %r', db_path)
            self._create_tables()
        return self

    def __exit__(self, *args, **kwargs):
        """
        Exits the context manager: closes the connection object.
        """
        self.conn.close()

    @staticmethod
    def get_db_path():
        """
        Gets the path to the index database.
        """
        return os.path.join(system.get_app_data_directory(), DB_FILE_NAME)

    # ---------------------------------------------------------------
    # Project management
    # ---------------------------------------------------------------
    def create_project(self, project_path):
        """
        Creates a project. If the project does already exists, the method
        simply returns it's project id.

        A project is just a path that will get scanned recursively to build
        the file and symbol index.

        :param project_path: path of the project to create.
        :return: PROJECT_ID
        """
        sql = "INSERT INTO Project(PROJECT_PATH, PROJECT_NAME) VALUES(?, ?);"
        if not self.has_project(project_path):
            project_name = os.path.split(project_path)[1]
            c = self.conn.cursor()
            DbHelper.exec_sql(c, sql, project_path, project_name)
            self.conn.commit()
            return self._get_last_insert_row_id(c)
        else:
            p = self.get_project(project_path)
            return int(p[COL_PROJECT_ID])

    def has_project(self, project_path):
        """
        Checks if the project exists in the database.

        :param project_path: path of the project to check.

        :returns: True if the file has been added to the db.
        """
        statement = 'SELECT COUNT(*) FROM Project WHERE PROJECT_PATH = ?;'
        c = self.conn.cursor()
        DbHelper.exec_sql(c, statement, project_path)
        results = c.fetchone()
        count = 0
        if results:
            count = results['COUNT(*)']
        return count > 0

    def get_projects(self):
        """
        Gets the complete list of indexed projects.
        """
        c = self.conn.cursor()
        statement = 'SELECT * FROM Project;'
        DbHelper.exec_sql(c, statement)
        while True:
            row = c.fetchone()
            if row is None:
                return
            yield row

    def get_project(self, project_path):
        """
        Gets a Project item.

        :param project_path: path of the project item to retrieve.
        """
        c = self.conn.cursor()
        statement = 'SELECT * FROM Project WHERE PROJECT_PATH = ?'
        DbHelper.exec_sql(c, statement, project_path)
        return c.fetchone()

    def delete_project(self, project_path):
        """
        Delete a project from the index database (all associated files and
        symbols will be deleted).

        :param project_path: path
        """
        proj = self.get_project(project_path)
        if proj is None:
            return False
        pid = proj[COL_PROJECT_ID]
        statement = 'DELETE FROM Project where PROJECT_ID = ?;'
        c = self.conn.cursor()
        DbHelper.exec_sql(c, statement, pid)
        statement = 'DELETE FROM File where PROJECT_ID = ?;'
        c = self.conn.cursor()
        DbHelper.exec_sql(c, statement, pid)
        statement = 'DELETE FROM Symbol where PROJECT_ID = ?;'.format(pid)
        c = self.conn.cursor()
        DbHelper.exec_sql(c, statement, pid)
        self.conn.commit()
        return True

    # ---------------------------------------------------------------
    # File management
    # ---------------------------------------------------------------
    # FILE CRUD Operations
    def create_file(self, file_path, project_id, commit=True):
        """
        Creates a file.

        If the file does already exists, the method simply returns the file id.

        :param file_path: Path of the file to create
        :param project_id: Id of the parent project.

        :returns: FILE_ID
        """
        sql = "INSERT INTO File(FILE_PATH, FILE_NAME, PROJECT_ID) " \
              "VALUES(?, ?, ?);"
        if not self.has_file(file_path):
            file_name = os.path.split(file_path)[1]
            c = self.conn.cursor()
            DbHelper.exec_sql(c, sql, file_path, file_name, project_id)
            fid = self._get_last_insert_row_id(c)
            # add to file index
            searchable_name = self._get_searchable_name(file_name)
            sql = "INSERT INTO File_index(FILE_ID, CONTENT) VALUES(?, ?);"
            DbHelper.exec_sql(c, sql, fid, searchable_name)
            if commit:
                self.conn.commit()
            return fid
        else:
            f = self.get_file_by_path(file_path)
            return int(f[COL_FILE_ID])

    def update_file(self, file_path, mtime, new_path=None, commit=True):
        """
        Updates a file in the database.

        :param file_path: Path of the file to update.
        :param mtime: The new modification time of the file.
        :param new_path: The new file path. None to specify the path/name
            has not changed.

        :raises: ValueError if the file_path is not in the db.
        """
        file_row = self.get_file_by_path(file_path)
        if file_row is None:
            raise ValueError('invalid file path')
        if new_path is None:
            new_path = file_path
        file_name = os.path.split(new_path)[1]
        fid = file_row[COL_FILE_ID]
        c = self.conn.cursor()
        sql = 'UPDATE File SET FILE_TIME_STAMP=?, FILE_PATH = ?, ' \
            'FILE_NAME = ? WHERE FILE_ID = ?;'
        DbHelper.exec_sql(c, sql, mtime, new_path, file_name, fid)
        if commit:
            self.conn.commit()

    def delete_file(self, file_path, commit=True):
        """
        Deletes a file from the index.

        :param file_path: Path of the file to remove.
        :raises: ValueError if the file_path does not exists in the database
        """
        file_row = self.get_file_by_path(file_path)
        if file_row is None:
            return False
        fid = file_row[COL_FILE_ID]
        c = self.conn.cursor()
        statement = 'DELETE FROM File where FILE_ID = ?'
        DbHelper.exec_sql(c, statement, fid)
        statement = 'DELETE FROM Symbol where FILE_ID = ?'
        DbHelper.exec_sql(c, statement, fid)
        if commit:
            self.conn.commit()
        return True

    # Utility methods related to files management
    def has_file(self, file_path):
        """
        Checks if the file exists in the database.

        :returns: True if the file has been added to the db.
        """
        statement = 'SELECT COUNT(*) FROM FILE WHERE FILE_PATH = ?;'
        c = self.conn.cursor()
        DbHelper.exec_sql(c, statement, file_path)
        results = c.fetchone()
        count = 0
        if results:
            count = results['COUNT(*)']
        return count > 0

    def get_files(self, project_ids=None, name_filter=''):
        """
        Generates the list of all files found in the index.

        Client code can specify to only look into the specified projects and
        apply a name filter.

        :param project_ids: the list of project ids to look into.
                            Use None the gets the whole list of files, across
                            projects.
        :param name_filter: optional name filter to apply.
        """
        searchable_name = '*%s*' % self._get_searchable_name(name_filter)
        c = self.conn.cursor()
        if project_ids:
            # look into specified project files
            project_ids = str(tuple(project_ids)).replace(',)', ')')
            if name_filter:
                self.conn.create_function('MATCH_RATIO', 2, match_ratio)
                sql = 'SELECT * FROM File WHERE PROJECT_ID IN %s AND ' \
                      'FILE_ID IN ( SELECT FILE_ID FROM File_index WHERE ' \
                      'CONTENT MATCH ?) ' \
                      'ORDER BY MATCH_RATIO(FILE_NAME, ?) ASC;' % project_ids
                DbHelper.exec_sql(c, sql, searchable_name, name_filter)
            else:
                sql = 'SELECT * FROM File WHERE PROJECT_ID IN %s ' \
                    'ORDER BY FILE_NAME ASC;' % project_ids
                DbHelper.exec_sql(c, sql)
        else:
            # look into all files, across all projects
            if name_filter:
                self.conn.create_function('MATCH_RATIO', 2, match_ratio)
                sql = 'SELECT * FROM File ' \
                    'WHERE FILE_ID IN ( SELECT FILE_ID FROM File_index WHERE '\
                    'CONTENT MATCH ?) ORDER BY MATCH_RATIO(FILE_NAME, ?) ASC;'
                DbHelper.exec_sql(c, sql, searchable_name, name_filter)
            else:
                sql = 'SELECT * FROM File ORDER BY FILE_NAME ASC;'
                DbHelper.exec_sql(c, sql)
        while True:
            row = c.fetchone()
            if row is None:
                return
            yield row

    def get_file_mtime(self, file_path):
        """
        Gets the file's modification time from the db

        :returns: mtime - float

        :raises: ValueError if the file_path does not exists in the database
        """
        file_row = self.get_file_by_path(file_path)
        if file_row is None:
            raise ValueError('invalid file path: %s' % file_path)
        return file_row[COL_FILE_TIME_STAMP]

    def get_file_by_path(self, path):
        """
        Gets a File row from path
        """
        c = self.conn.cursor()
        statement = 'SELECT * FROM File WHERE FILE_PATH = ?'
        DbHelper.exec_sql(c, statement, path)
        return c.fetchone()

    def get_file_by_id(self, fid):
        """
        Returns a file item by ID.

        :param fid: id of the file to retrieve.
        """
        c = self.conn.cursor()
        statement = 'SELECT * FROM File WHERE FILE_ID = ?'
        DbHelper.exec_sql(c, statement, fid)
        return c.fetchone()

    # ---------------------------------------------------------------
    # File management
    # ---------------------------------------------------------------
    # FILE CRUD Operations
    def create_symbol(self, name, line, column, icon_theme, icon_path,
                      file_id, project_id, parent_symbol_id=None, commit=True):
        """
        Adds a symbol to the database.

        :param name: name of the symbol
        :param line: line where the symbol is defined
        :param column: column where the symbol is defined
        :param icon_theme: icon from theme that will be used when displaying
            the symbol
        :param icon_path: icon from path that will be used when displaying
            the symbol
        :param file_id: Id of the file where the symbol can be found
        :param parent_symbol_id: Optional parent symbol id

        returns: symbol id that can be used to add child symbols.
        """
        if parent_symbol_id is None:
            parent_symbol_id = 'null'

        statement = ('INSERT INTO Symbol(SYMBOL_LINE, SYMBOL_COLUMN, '
                     'SYMBOL_ICON_THEME, SYMBOL_ICON_PATH, SYMBOL_NAME, '
                     'FILE_ID, PARENT_SYMBOL_ID, PROJECT_ID) '
                     'values (?, ?, ?, ?, ?, ?, ?, ?);')
        c = self.conn.cursor()
        DbHelper.exec_sql(c, statement, line, column, icon_theme, icon_path,
                          name, file_id, str(parent_symbol_id), project_id)
        sid = self._get_last_insert_row_id(c)
        sql = "INSERT INTO Symbol_index(SYMBOL_ID, CONTENT) VALUES(?, ?);"
        DbHelper.exec_sql(c, sql, sid, self._get_searchable_name(name))
        if commit:
            self.conn.commit()
        return sid

    def delete_file_symbols(self, file_id):
        """
        Removes all symbols found in the specified file_id.

        :param file_id: id of the file that contains the symbols to remove.

        .. note:: there is no update of a symbol, symbols are always entirely
            removed from db before the updated symbols are inserted.
        """
        c = self.conn.cursor()
        statement = 'DELETE FROM Symbol where FILE_ID = ?'
        DbHelper.exec_sql(c, statement, file_id)
        self.conn.commit()

    def get_symbols(self, file_id=None, name_filter='', project_ids=None):
        """
        Generates a filtered list of all symbol names (using fuzzy matching)
        found in the index.

        Client code can specify to look into the symbols of the specified
        projects or the specified file.

        .. note:: Both ``file_id`` and ``project_ids`` cannot be used together,
            ``file_id`` has the biggest priority.

        :param file_id: Id of the file to look into.
        :param project_ids: Id of the projects to look into.
            Discarded if file_id is not None.
        :param name_filter: Optional filter to apply on every symbol name.

        :returns: Generator that yield Symbol items.
        """
        c = self.conn.cursor()
        searchable_name = '*%s*' % self._get_searchable_name(name_filter)
        if file_id:
            # get file symbols
            if name_filter:
                self.conn.create_function('MATCH_RATIO', 2, match_ratio)
                sql = 'SELECT * FROM Symbol WHERE FILE_ID = ? AND ' \
                      'SYMBOL_ID IN ( SELECT SYMBOL_ID FROM Symbol_index ' \
                      'WHERE CONTENT MATCH ?) ' \
                      'ORDER BY MATCH_RATIO(SYMBOL_NAME, ?) ASC;'
                self.exec_sql(c, sql, file_id, searchable_name, name_filter)
            else:
                sql = 'SELECT * FROM Symbol WHERE FILE_ID = ? ' \
                    'ORDER BY SYMBOL_NAME ASC;'
                self.exec_sql(c, sql, file_id)
        elif project_ids:
            # get project symbols
            project_ids = str(tuple(project_ids)).replace(',)', ')')
            if name_filter:
                self.conn.create_function('MATCH_RATIO', 2, match_ratio)
                sql = 'SELECT * FROM Symbol ' \
                      'WHERE Symbol.PROJECT_ID IN %s AND ' \
                      'Symbol.SYMBOL_ID IN ( ' \
                      'SELECT SYMBOL_ID FROM Symbol_index ' \
                      'WHERE CONTENT MATCH ?)' \
                      'ORDER BY MATCH_RATIO(Symbol.SYMBOL_NAME, ?) ASC;' % \
                      project_ids
                self.exec_sql(c, sql, searchable_name, name_filter)
            else:
                sql = 'SELECT * FROM Symbol ' \
                      'WHERE Symbol.PROJECT_ID IN %s ' \
                      'ORDER BY Symbol.SYMBOL_NAME ASC;' % project_ids
                self.exec_sql(c, sql)
        else:
            # get all symbols
            if name_filter:
                self.conn.create_function('MATCH_RATIO', 2, match_ratio)
                sql = 'SELECT * FROM Symbol ' \
                      'WHERE SYMBOL_ID IN ( ' \
                      'SELECT SYMBOL_ID FROM Symbol_index ' \
                      'WHERE CONTENT MATCH ?)' \
                      'ORDER BY MATCH_RATIO(SYMBOL_NAME, ?) ASC;'
                DbHelper.exec_sql(c, sql, searchable_name, name_filter)
            else:
                sql = 'SELECT * FROM Symbol ORDER BY SYMBOL_NAME ASC;'
                DbHelper.exec_sql(c, sql)
        while True:
            row = c.fetchone()
            if row is None:
                return
            yield row

    def _create_tables(self):
        """
        Creates the two index tables: one for the file index and one for the
        symbol index.
        """
        c = self.conn.cursor()
        for statement in SQL_CREATE_TABLES:
            DbHelper.exec_sql(c, statement)
        self.conn.commit()

    @staticmethod
    def _get_last_insert_row_id(c):
        """
        Gets the last insert row id.
        :param c: sqlite3.Cursor
        :return: int
        """
        DbHelper.exec_sql(c, "SELECT last_insert_rowid();")
        return int(c.fetchone()['last_insert_rowid()'])

    @staticmethod
    def _get_searchable_name(name):
        """
        Replaces capital letters by _ + small letter if name is camel/pascal
        case.

        :param name: name to convert
        :return: converted name
        """
        if DbHelper.is_camel_case(name):
            v = ''.join([('_' + l.lower()) if l.isupper() else l
                         for l in name])
        else:
            v = name
        return v

    @staticmethod
    def is_camel_case(name):
        """
        Checks if a name is camel case (or pascal case).
        """
        return bool(DbHelper.prog_camel_case.findall(name))

    @staticmethod
    def exec_sql(cursor, statement, *args):
        try:
            cursor.execute(statement, args)
        except sqlite3.OperationalError as e:
            _logger().warn('failed to executed SQL statement: %r. Args=%r - '
                           'Error = %s', statement, args, str(e))


def match_ratio(item, expr):
    """
    MATCH_RATIO function that will be added to sqlite in order to sort the
    filter list of symbols/files using fuzzy matching.

    Computes the edit distance between the given expr (user input) and an item
    from the db.
    """
    try:
        index = item.lower().index(get_search_tokens(expr)[0])
    except ValueError:
        ratio = sys.maxsize
    else:
        ratio = index - len(expr) / len(item)
    return ratio


def get_search_tokens(expr):
    return expr.lower().replace('_', ' ').replace('-', ' ').replace(
        '.', ' ').split(' ')


def _logger():
    return logging.getLogger(__name__)
