# -*- coding: utf-8 -*-
import copy
import re
import sqlite3
import types
from malibu.database import dbtypeconv

__doc__ = """
malibu.database.dbmapper
------------------------

This is a small, hackish ORM for SQLite3.


Note from the author: (01 / 14 / 2016)
--------------------------------------

I've got to be honest, this is probably the worst code I have ever written and read.
At this point, this code is so difficult to maintain and keep up to date for 2/3 compat that
it is almost not worth the work.
Especially considering that there are things like Peewee, SQLAlchemy, etc, this is not worth
using or maintaining.

From this point forward, I recommend using some other, cleaner, better maintained solution
such as Peewee.
This DBMapper code will no longer be maintained and will be deprecated starting
with the 0.1.6 release.
The code will be removed as the 1.0.0 release approaches.
There may be plans to replace this with a SQLite adapter for the malibu.design.brine series
of classes that behave similar to this, just without all the cruft.
"""


class DBMapper(object):
    """ This is code for a relatively small ORM for SQLite built
        on top of the python-sqlite3 module.
    """

    # FETCH Constants for __execute()

    FETCH_ONE = 'one'
    FETCH_MANY = 'many'
    FETCH_ALL = 'all'

    # INDEX Constants for options dictionary.

    INDEX_PRIMARY = 'primaryIndex'
    INDEX_AUTOINCR = 'autoincrIndex'
    INDEX_UNIQUE = 'uniqueIndices'
    GENERATE_FTS_VT = 'genFTSVTs'

    # Global variables for static database methods

    _options = None
    __default_options = {
        INDEX_PRIMARY: 0,
        INDEX_AUTOINCR: True,
        INDEX_UNIQUE: set(),
        GENERATE_FTS_VT: False  # Do NOT generate FTS by default.
    }

    @staticmethod
    def get_default_options():
        """ DBMapper.get_default_options()

            Returns a deep copy of the default options dictionary for
            modification in subclasses.
        """

        return copy.deepcopy(DBMapper.__default_options)

    @staticmethod
    def connect_database(dbpath):
        """ DBMapper.connect_database(dbpath)

            Connects to a database at 'dbpath' and installs the json
            type converter "middleware" into the database system.
        """

        dbtypeconv.install_json_converter()
        __db = sqlite3.connect(dbpath, detect_types=sqlite3.PARSE_DECLTYPES)

        return __db

    @classmethod
    def set_db_options(cls, db, keys, ktypes, options=__default_options):
        """ DBMapper.set_db_options(db       => database instance
                                    keys     => list of keys
                                    ktypes   => list of key types
                                    options  => options dictionary (optional))

            Sets options for a subclasses DBMapper context.
        """

        if cls._options is None:
            cls._options = {}
            cls._options['database'] = db
            cls._options['keys'] = keys
            cls._options['keytypes'] = ktypes
            cls._options['options'] = options
        else:
            cls._options['database'] = db
            cls._options['keys'] = keys
            cls._options['keytypes'] = ktypes

    @classmethod
    def load(cls, **kw):
        """ DBMapper.load(**kw)

            Loads a *single* row from the database and populates it into
            the context cls this method was called under.

            If the database returns more than one row for the kwarg query,
            this method will only return the first result! If you want a
            list of matching rows, use find() or search().
        """

        if cls._options is None:
            raise DBMapperException(
                'Static database options have not been set.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()

        keys = []
        vals = []
        for key, val in kw.items():
            keys.append(key)
            vals.append(val)
        whc = []
        for pair in zip(keys, vals):
            whc.append("%s=?" % (pair[0]))
        query = "select * from %s where (%s)" % (obj._table, ' and '.join(whc))
        result = obj.__execute(cur, query, args=vals)
        if result is None:
            for key in dbo['keys']:
                setattr(obj, "_%s" % (key), None)
            return
        for key, dbv in zip(dbo['keys'], result):
            setattr(obj, "_%s" % (key), dbv)

        return obj

    @classmethod
    def new(cls, **kw):
        """ DBMapper.new(**kw)

            Creates a new contextual instance and returns the object.
            Only parameters defined in the kwargs will be passed in to
            the record creation query, as there is no support for default
            values yet. (06/11/15)
        """

        if cls._options is None:
            raise DBMapperException(
                'Static database options have not been set.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()

        keys = []
        vals = []
        for key, val in kw.items():
            keys.append(key)
            vals.append(val)
        anonvals = []
        for val in vals:
            anonvals.append('?')
        query = "insert into %s (%s) values (%s)" % (
            obj._table, ','.join(keys), ','.join(anonvals))
        obj.__execute(cur, query, args=vals)

        res = cls.find(**kw)
        if len(res) == 0:
            return None
        else:
            return res[0]

    @classmethod
    def find(cls, **kw):
        """ DBMapper.find(**kw)

            Searches for a set of records that match the query built by
            the contents of the kwargs and returns a filterable list of
            contextualized results that can be modified.
        """

        if cls._options is None:
            raise DBMapperException(
                'Static database options have not been set.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()
        primaryKey = dbo['keys'][dbo['options'][DBMapper.INDEX_PRIMARY]]

        keys = []
        vals = []
        for key, val in kw.items():
            keys.append(key)
            vals.append(val)
        whc = []
        for pair in zip(keys, vals):
            whc.append('%s=?' % (pair[0]))
        query = "select %s from %s where (%s)" % (
            primaryKey, obj._table, ' and '.join(whc))
        result = obj.__execute(cur, query, args=vals, fetch=DBMapper.FETCH_ALL)

        load_pairs = []
        for row in result:
            load_pairs.append(
                {primaryKey: row[dbo['options'][DBMapper.INDEX_PRIMARY]]}
            )

        return DBResultList([cls.load(**pair) for pair in load_pairs])

    @classmethod
    def find_all(cls):
        """ DBMapper.find_all()

            Finds all rows that belong to a table and returns a filterable
            list of contextualized results. Please note that the list that
            is returned can be empty, but it should never be none.
        """

        if cls._options is None:
            raise DBMapperException(
                'Static database options have not been set.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()
        primaryKey = dbo['keys'][dbo['options'][DBMapper.INDEX_PRIMARY]]

        query = "select %s from %s" % (primaryKey, obj._table)
        result = obj.__execute(cur, query, fetch=DBMapper.FETCH_ALL)

        load_pairs = []
        for row in result:
            load_pairs.append(
                {primaryKey: row[dbo['options'][DBMapper.INDEX_PRIMARY]]}
            )

        return DBResultList([cls.load(**pair) for pair in load_pairs])

    @classmethod
    def search(cls, param):
        """ DBMapper.search(param)

            This function will return a list of results that match the given
            param for a full text query. The search parameter should be in the
            form of a sqlite full text query, as defined here:
              http://www.sqlite.org/fts3.html#section_3

            As an example, suppose your table looked like this:

              +----+---------+----------------+
              | id |   name  |    description |
              +----+---------+----------------+
              | 1  |  linux  |   some magic   |
              | 2  | freebsd | daemonic magic |
              | 3  | windows |   tomfoolery   |
              +----+---------+----------------+

            A full text query for "name:linux magic" would return the first
            row because the name is linux and the description contains "magic".
            A full text query just for "description:magic" would return both
            rows one and two because the descriptions contain the word "magic".
        """

        if cls._options is None:
            raise DBMapperException(
                'Static database options have not been set.')

        if not cls._options['options'][DBMapper.GENERATE_FTS_VT]:
            raise DBMapperException(
                'Full-text search table not enabled on this table.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()

        query = """select docid from _search_%s where _search_%s match \"?\"""" % \
                (obj._table, obj._table)

        result = obj.__execute(
            cur,
            query,
            args=[param],
            fetch=DBMapper.FETCH_ALL)

        load_pairs = []
        for row in result:
            load_pairs.append({cls._options['keys'][0]: row[0]})

        return DBResultList([cls.load(**pair) for pair in load_pairs])

    @classmethod
    def join(cls, cond, a, b):
        """ DBMapper.join(cond => other table to join on
                          a    => left column to join
                          b    => right column to join)

            Performs a sqlite join on two tables. Returns the join results
            in a filterable list.
        """

        if cls._options is None or cond._options is None:
            raise DBMapperException(
                'Static database options have not been set.')

        dba = cls._options
        obja = cls(dba['database'])
        dbb = cond._options
        objb = cond(dbb['database'])
        cur = dba['database'].cursor()
        primaryKeyA = dba['keys'][dba['options'][DBMapper.INDEX_PRIMARY]]
        primaryKeyB = dbb['keys'][dba['options'][DBMapper.INDEX_PRIMARY]]

        query = "select A.%s, B.%s from %s as A join %s as B on A.%s=B.%s" % (
                primaryKeyA, primaryKeyB, obja._table, objb._table, a, b)
        result = obja.__execute(cur, query, fetch=DBMapper.FETCH_ALL)

        load_pair_a = []
        load_pair_b = []
        for row in result:
            load_pair_a.append({primaryKeyA: row[0]})
            load_pair_b.append({primaryKeyB: row[1]})

        return (
            DBResultList([cls.load(**pair) for pair in load_pair_a]),
            DBResultList([cond.load(**pair) for pair in load_pair_b]),
        )

    def __init__(self, db, keys, keytypes, options=__default_options):

        self._db = db
        self._options = options
        if 'tableName' not in self._options:
            self._table = self.__class__.__name__.lower()
        else:
            self._options['tableName']

        self._keys = keys
        self._keytypes = keytypes

        self._primary_ind = self._options[DBMapper.INDEX_PRIMARY]
        self._autoincr_ind = self._options[DBMapper.INDEX_AUTOINCR]
        self._primary = self._keys[self._primary_ind]
        self._unique_keys = self._options[DBMapper.INDEX_UNIQUE]

        self.__generate_structure()
        self.__generate_getters()
        self.__generate_setters()
        self.__generate_properties()

    def __execute(self, cur, sql, fetch=FETCH_ONE, limit=-1, args=()):
        """ __execute(self,
                      cur      => pointer to database cursor
                      sql      => sql query to execute
                      fetch    => amount of results to fetch
                      limit    => query limit if not use FETCH_ONE
                      args     => query arguments to parse in)

            Filters, quotes, and executes the provided sql query and returns
            a list of database rows.
        """

        query = sql
        try:
            if len(args) >= 1:
                cur.execute("select " + ", ".join(["quote(?)" for i in args]),
                            args)
                quoted_values = cur.fetchone()
                for quoted_value in quoted_values:
                    query = query.replace('?', str(quoted_value), 1)
        except:
            pass

        try:
            cur.execute(query)
        except (sqlite3.ProgrammingError):
            try:
                cur.execute(query, args)
            except Exception as e:
                raise DBMapperException(
                    "Error while executing query [%s]" % (query), cause=e)
        except Exception as e:
            raise DBMapperException(
                "Error while executing query [%s]" % (query), cause=e)

        if fetch == DBMapper.FETCH_ONE:
            return cur.fetchone()
        elif fetch == DBMapper.FETCH_MANY:
            if limit == -1:
                limit = cur.arraysize
            return cur.fetchmany(size=limit)
        elif fetch == DBMapper.FETCH_ALL:
            return cur.fetchall()
        else:
            return cur.fetchall()

    def __get_table_info(self, table=None):
        """ __get_table_info(self, table)

            Returns pragma information for a table.
        """

        table = self._table if table is None else table
        cur = self._db.cursor()
        query = "pragma table_info(%s)" % (table)

        return self.__execute(cur, query, fetch=DBMapper.FETCH_ALL)

    def __generate_structure(self):
        """ __generate_structure(self)

            Generates table structure for determining column updates and
            search information.
        """

        # use pragma constructs to get table into
        tblinfo = self.__get_table_info()

        # create the table if the statement does not exist
        if len(tblinfo) == 0:
            ins = zip(self._keys, self._keytypes)
            typarr = []
            for pair in ins:
                if pair[0] == self._primary:
                    # identifier type primary key
                    if self._autoincr_ind:
                        typarr.append("%s %s primary key autoincrement" % (
                            pair[0], pair[1]))
                    else:
                        typarr.append("%s %s primary key" % (pair[0], pair[1]))
                elif pair[0] in self._unique_keys:
                    typarr.append("%s %s unique" % (pair[0], pair[1]))
                else:
                    # identifier type
                    typarr.append("%s %s" % (pair[0], pair[1]))
            cur = self._db.cursor()
            # create table if not exists <table> (<typarr>)
            query = "create table if not exists %s (%s)" % \
                (self._table, ', '.join(typarr))
            self.__execute(cur, query)

        # make sure table columns are up to date.
        if len(tblinfo) > 0:
            # use pragma table info to build database schema
            schema_ids = []
            schema_types = []
            for col in tblinfo:
                schema_ids.append(col[1])
                schema_types.append(col[2])
            # use schema to determine / apply database updates
            schema_updates = []
            for pair in zip(self._keys, self._keytypes):
                if pair[0] in schema_ids:
                    continue
                else:
                    schema_updates.append("%s %s" % (pair[0], pair[1]))
            for defn in schema_updates:
                query = "alter table %s add column %s" % (self._table, defn)
                cur = self._db.cursor()
                self.__execute(cur, query)

        # generate full text search table that corresponds with this dbo
        if self._options[DBMapper.GENERATE_FTS_VT]:
            if len(self.__get_table_info("_search_%s" % (self._table))) == 0:
                cur = self._db.cursor()
                # fts4 table doesn't exist, make it.
                query = "create virtual table _search_%s using fts4(%s, content='%s')" % \
                        (self._table, ','.join(self._keys), self._table)
                self.__execute(cur, query)
                # create pre/post update/delete triggers for cascading updates
                # XXX - [trigger warning] DO WE NEED THE TRIGGERS
                query = "create trigger _%s_bu before update on %s begin delete from _search_%s where docid=old.rowid; end;" % \
                        (self._table, self._table, self._table)
                self.__execute(cur, query)
                query = "create trigger _%s_bd before delete on %s begin delete from _search_%s where docid=old.rowid; end;" % \
                        (self._table, self._table, self._table)
                self.__execute(cur, query)
                search_keys = ','.join(['docid'] + self._keys[1:])
                target_keys = ','.join(['new.' + vkey for vkey in self._keys])
                query = "create trigger _%s_au after update on %s begin insert into _search_%s(%s) values(%s); end;" % \
                        (self._table, self._table, self._table, search_keys,
                         target_keys)
                self.__execute(cur, query)
                query = "create trigger _%s_ai after insert on %s begin insert into _search_%s(%s) values(%s); end;" % \
                        (self._table, self._table, self._table, search_keys,
                         target_keys)
                self.__execute(cur, query)

        self._db.commit()

    def __generate_getters(self):
        """ __generate_getters(self)

            Generates magical getter methods for pull data from the
            underlying database.
        """

        for _key in self._keys:
            def getter_templ(self, __key=_key):
                if __key not in self._keys:
                    return
                cur = self._db.cursor()
                # select * from table where key=<key>
                query = "select %s from %s where %s=?" % (
                    __key, self._table, self._primary)
                result = self.__execute(
                    cur,
                    query,
                    args=(getattr(self, "_%s" % (self._primary)),))
                try:
                    return result[0]
                except:
                    return result
            setattr(self, "get_" + _key, types.MethodType(getter_templ, self))

    def __generate_setters(self):

        for _key in self._keys:
            def setter_templ(self, value, __key=_key):
                if __key not in self._keys:
                    return
                cur = self._db.cursor()
                # update table set key=value where primary=id
                query = "update %s set %s=? where %s=?" % (
                    self._table, __key, self._primary)
                self.__execute(
                    cur,
                    query,
                    args=(value, getattr(self, "_%s" % (self._primary)),))
                self._db.commit()
                setattr(self, "_%s" % (__key), value)
            setattr(self, "set_" + _key, types.MethodType(setter_templ, self))

    def __generate_properties(self):

        for _key in self._keys:
            setattr(self, "_%s" % (_key), None)

        for _key in self._keys:
            getf = getattr(self, "get_%s" % (_key))
            setf = getattr(self, "set_%s" % (_key))
            setattr(self, _key, property(getf, setf, None, "[%s] property"))

    def create(self):

        cur = self._db.cursor()
        vals = []
        for key in self._keys:
            if key == self._primary and self._autoincr_ind:
                vals.append(None)  # Put None in for the index because autoinc
            else:
                vals.append(getattr(self, "_%s" % (key)))
        qst = ', '.join(["?" for item in vals])
        query = "insert into %s values (%s)" % (self._table, qst)
        self.__execute(cur, query, args=vals)
        setattr(self, "_%s" % (self._primary), cur.lastrowid)

    def delete(self):

        cur = self._db.cursor()

        qst = "%s=?" % (self._keys[self._primary_ind])
        primary_val = getattr(self, "_%s" % (self._keys[self._primary_ind]))

        query = "delete from %s where (%s)" % (self._table, qst)
        self.__execute(cur, query, args=(primary_val,))


class DBResultList(list):

    def __init__(self, extend=None):

        if isinstance(extend, list):
            for item in extend:
                if isinstance(item, DBMapper):
                    self.append(item)
                else:
                    continue

    def filter_equals(self, key, val):
        """ filter_equals(key, val) ->
              filters database find result based on
              key-value equality.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if getattr(dbo, "_%s" % (key)) == val:
                    res.append(dbo)
                else:
                    continue
            except:
                continue

        return res

    def filter_iequals(self, key, val):
        """ filter_iequals(key, val) ->
              filters database find result based on
              case insensitive key-value equality.
              assumes that db attribute and val are strings.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if getattr(dbo, "_%s" % (key)).lower() == val.lower():
                    res.append(dbo)
                else:
                    continue
            except:
                continue

        return res

    def filter_inequals(self, key, val):
        """ filter_inequals(key, val) ->
              filters database find result based on
              key-value inequality.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if getattr(dbo, "_%s" % (key)) != val:
                    res.append(dbo)
                else:
                    continue
            except:
                continue

        return res

    def filter_regex(self, key, regex):
        """ filter_regex(key, regex) ->
              filters database find result based on
              regex value matching.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if re.match(regex, getattr(dbo, "_%s" % (key))) is not None:
                    res.append(dbo)
                else:
                    continue
            except:
                continue

        return res


class DBMapperException(Exception):

    def __init__(self, message, cause=None):

        if cause is not None:
            super(DBMapperException, self).__init__(
                message + u', caused by ' + repr(cause))
        elif cause is None:
            super(DBMapperException, self).__init__(message)

        self.message = message
        self.cause = cause

    def __str__(self):

        return repr(self.message) + u', caused by ' + repr(self.cause)
