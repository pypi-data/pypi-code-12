"""
A simple relational database interface that stays out of your way.
Designed to be small, fast, and transparent. Integrates with user-defined record classes.

* Record:     base class for user-defined Record classes (inherits from bl.dict.Dict)
* RecordSet:  set of Records (inherits from list)
* Database :  a database connection
                (init with a standard DB-API 2.0 connection string)

---------------------------------------------------------------------------
                                            Memory:  Footprint:
# > python                                  4656 K   4656 K (Python 3.4.3 osx)
# >>> from bl.database import Database      5460 K    804 K (YMMV)
---------------------------------------------------------------------------
Sample session: 
>>> d = Database()      # in-memory sqlite3 database
>>> d.execute("create table table1 (name varchar primary key, email varchar not null unique)")
>>> d.execute("insert into table1 (name, email) values ('sah', 'sah@blackearthgroup.com')")
>>> records = d.select("select * from table1")
>>> records[0].name
'sah'
>>> d.connection.close()
>>>
"""

import datetime, imp, re, time
from bl.dict import Dict
from bl.log import Log

class Database(Dict):
    """a database connection object."""

    def __init__(self, connection_string=None, dba=None, connection=None, tries=3, debug=False, log=Log(), **args):
        Dict.__init__(self, 
            connection_string=re.sub('\s+', ' ', connection_string or ''),
            connection=connection,
            dba=dba, 
            debug=debug, tries=tries, log=log, **args)
        if self.connection is not None:
            self.dba = self.connection.__module__
        elif self.dba is None:
            import sqlite3
            self.dba = sqlite3
        elif type(self.dba) in (str, bytes):
            fm = imp.find_module(dba)
            self.dba = imp.load_module(self.dba, fm[0], fm[1], fm[2])

        # if self.dba.__module__ == 'psycopg2':
        #     # make psycopg2 always return unicode strings
        #     try:
        #         dba.extensions.register_type(dba.extensions.UNICODE)
        #         dba.extensions.register_type(dba.extensions.UNICODEARRAY)                    
        #     except:
        #         # if that didn't work for some reason, then just go with the default setup.
        #         pass
            
        # try reaching the db "tries" times, with increasing wait times, before raising an exception.
        if self.connection is None:
            for i in range(tries):
                try: 
                    if self.connection_string != None:
                        print(dba.connect, self.connection_string)
                        self.connection = self.dba.connect(self.connection_string)
                    else:
                        print(dba.connect, args)
                        self.connection = self.dba.connect(**args)
                    break
                except: 
                    if i==list(range(tries))[-1]:       # last try failed
                        raise
                    else:                               # wait a bit
                        time.sleep(2*i)                 # doubling the time on each wait
        try:
            if self.dba == 'sqlite3' or self.dba.__module__ == 'sqlite3':
                self.execute("pragma foreign_keys = ON")
        except:
            pass

    def __repr__(self):
        return "Database(dba=%s, connection_string='%s')" % (self.dba, self.connection_string)

    def migrate(self, migrations=None):
        from .migration import Migration
        Migration.migrate(self, migrations_path=migrations or self.migrations, log=self.log)

    def cursor(self):
        """get a cursor for fine-grained transaction control."""
        cursor = self.connection.cursor()
        return cursor

    def execute(self, sql, vals=None, cursor=None):
        """execute SQL transaction, commit it, and return nothing. 
        If a cursor is specified, work within that transaction.
        """
        if self.debug==True: self.log(sql)
        try:
            c = cursor or self.connection.cursor()
            if vals in [None, (), [], {}]:
                c.execute(sql)
            else:
                c.execute(sql, vals)
            if cursor is None:
                self.commit()
        except:
            if cursor is not None:
                cursor.connection.rollback()
            raise

    def commit(self):
        """commit the changes on the current connection."""
        self.connection.commit()

    def rollback(self):
        """rollback the changes on the current connection, aborting the transaction."""
        self.connection.rollback()

    def select(self, sql, vals=None, Record=None, RecordSet=None, cursor=None):
        """select from db and return the full result set.
        Required Arguments:
            sql: the SQL query as a string
        Optional/Named Arguments
            vals: any bound variables
            Record: the class (itself) that the resulting records should be
        """
        if Record is None:
            from .record import Record
        if RecordSet is None:
            from .recordset import RecordSet

        records = RecordSet()                   # Populate a RecordSet (list) with the all resulting
        for record in self.selectgen(sql, vals=vals, Record=Record, cursor=cursor):
            records.append(record)
        return records

    def selectgen(self, sql, vals=None, Record=None, cursor=None):
        """select from db and yield a generator"""
        c = cursor or self.cursor()
        self.execute(sql, vals=vals, cursor=c)

        if Record is None:
            from .record import Record

        # get a list of attribute names from the cursor.description
        attr_list = list()
        for r in c.description:
            attr_list.append(r[0])

        result = c.fetchone()
        while result is not None:
            record = Record(self)               # whatever the record class is, include another instance
            for i in range(len(attr_list)):     # make each attribute dict-able by name
                record[attr_list[i]] = result[i]
            yield record
            result = c.fetchone()

        if cursor is None:
            c.close()   # closing the cursor without committing rolls back the transaction.

    def select_one(self, sql, vals=None, Record=None, cursor=None):
        """select one record from db
        Required Arguments:
            sql: the SQL query as a string
        Optional/Named Arguments:
            vals: any bound variables
            Record: the class (itself) that the resulting records should be
        """
        c = cursor or self.cursor()
        self.execute(sql, vals, cursor=c)

        if Record is None:
            from .record import Record

        # get a list of attribute names from the cursor.description
        attr_list = list()
        for r in c.description:
            attr_list.append(r[0])
        result = c.fetchone()
        if result is None:
            record = None
        else:
            record = Record(self)
            for i in range(len(attr_list)):
                record[attr_list[i]] = result[i]
        if cursor is None:
            c.close()
        return record

    def quote(self, attr):
        """returns the given attribute in a form that is insertable in the insert() and update() methods."""
        t = type(attr)
        if t == type(None): return 'NULL'
        elif t == datetime.datetime:    # datetime -- put it in quotes
            return "'%s'" % str(attr)
        elif t == str:
            return self._quote_str(attr)
        elif t in [dict, Dict]:
            return "$$%s$$" % attr
        else:                           # boolean or number -- no quoting needed
            return str(attr).lower()

    def _quote_str(self, attr):
        """quote the attr string in a manner fitting the Database server, if known."""
        sn = self.servername().lower()
        if 'sqlserver' in sn or 'sqlite' in sn:
            # quote for sqlserver and sqlite: double '' to escape
            attr = "'" + re.sub("'", "''", attr) + "'"
        elif 'postgres' in sn:
            if type(attr) == str:
                attr = "$$%s$$" % attr
        else:
            if type(attr) == str:
                attr = "'%s'" % attr
            else:
                attr = "'%s'" % str(attr, 'UTF-8')
        return attr

    def servername(self):
        """return a string that describes the database server being used"""
        if type(self.dba) in [str, bytes]:
            return self.dba
        elif 'psycopg' in self.dba.__module__: 
            return 'postgresql'
        elif 'sqlite' in self.dba.__module__: 
            return 'sqlite'
        elif self.dbconfig is not None and self.dbconfig.server is not None:
            return self.dbconfig.server
        elif 'adodbapi' in str(self.connection): 
            return 'sqlserver'
        elif 'port=5432' in str(self.connection): 
            return 'postgresql'
        elif 'port=3306' in str(self.connection): 
            return 'mysql'
        else: 
            return ''
        
    def table_exists(self, table_name):
        sn = self.servername().lower()
        if 'sqlite' in sn:
            return self.select_one(
                "select * from sqlite_master where name=? and type='table' limit 1", (table_name,))
        elif 'mysql' in sn:
            return self.select_one(
                "show tables like %s", (table_name,))
        else:   
            # postgresql and sqlserver both use the sql standard here.
            return self.select_one(
                "select * from information_schema.tables where table_name=%s limit 1", (table_name,))

def doctests():
    """
    >>> d = Database()
    >>> d.execute("create table table1 (name varchar primary key, email varchar not null unique);")
    >>> d.execute("insert into table1 (name, email) values ('sah', 'sah@blackearthgroup.com')")
    >>> d.execute("insert into table1 (name, email) values ('sah', 'sah.harrison@gmail.com')")
    Traceback (most recent call last):
      ...
    sqlite3.IntegrityError: UNIQUE constraint failed: table1.name
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
