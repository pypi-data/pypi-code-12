# -*- coding: utf-8 -*-
import app.resources as rc
import model


class dbopen(object):
    """controller"""

    def __init__(self, database):
        """"""
        self._database = database
        super(dbopen, self).__init__()

    def __enter__(self):
        """Enter operation"""
        self.conn = self._database.open()
        return self.conn

    def __exit__(self, type, value, traceback):
        """"""
        if type is None:
            self._database.close(self.conn)
            return True
        return False


class rawquery(object):
    """controller"""
    def __init__(self, conn, sql):
        """"""
        self._conn = conn
        self._sql = sql
        super(rawquery, self).__init__()

    def __enter__(self):
        """"""
        self._conn.query(self._sql)
        self._data = self._conn.store_result()
        return self._data

    def __exit__(self, type, value, traceback):
        """"""
        if type is None:
            del self._data
            return True
        return False


class cursorquery(object):
    """controller"""
    def __init__(self, conn, sql):
        """"""
        self._conn = conn
        self._sql = sql
        super(cursorquery, self).__init__()

    def __enter__(self):
        """"""
        self._cur = self._conn.cursor()
        self._cur.execute(self._sql)
        return self._cur

    def __exit__(self, type, value, traceback):
        """"""
        if type is None:
            self._cur.close()
        return False



## From now, we start to handle different project flawors from handlers
class DatabaseProject(object):
    """Handles a database project"""

    def __init__(self, owner, **kwargs):
        """Initialize database project"""
        self._owner = owner
        self._database_host = kwargs.get('database_host', 'localhost')
        self._database_user = kwargs.get('database_user', 'root')
        self._database_password = kwargs.get('database_password', '')
        self._database_default = kwargs.get('database_default', '')
        super(DatabaseProject, self).__init__()
        # Update database schemas

    def Initialize(self):
        """Create first time. It's called from project container ctor'"""
        self._owner.schema_container = True
        self.CreateSchemas()
        self._owner.CreateTasks()

    def open(self):
        """Open connection"""
        import MySQLdb as driver
        return driver.connect(
            host=self._database_host,
            user=self._database_user,
            passwd=self._database_password)

    def close(self, conn):
        """close connection"""
        conn.close()

    def CreateSchemas(self):
        """Attempt to recover schemas from database and create it"""
        try:
            with dbopen(self) as conn:
                with rawquery(conn, 'SHOW SCHEMAS') as data:
                    if data:
                        kwargs = {'parent': self._owner}
                        for i in range(0, data.num_rows()):
                            kwargs['name'] = data.fetch_row()[0][0]
                            model.database.Schema(**kwargs)
                #Ok now we iterate over schemas and create tables
                for schema in self._owner[model.database.Schema]:
                    schema.CreateTables(conn)
                return True
        except:
            return False

    def get_kwargs(self):
        """get construction data"""
        return {
            'database_host': self._database_host,
            'database_user': self._database_user,
            'database_password': self._database_password,
            'database_default': self._database_default
        }

    def GetTabBitmap(self):
        """return tab bitmap"""
        return rc.GetBitmap('databases')

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('databases')


