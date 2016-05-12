#!/bin/env python
#-*- encoding=utf8 -*-
#
# Copyright 2014 zonehuang
#
# 作者：zonehuang
#
# 功能：该模块提供数据库访问的基类
# 
# 版本：V1.0.0
import copy
import itertools
import logging
import time
import re

try:
    import MySQLdb.constants
    import MySQLdb.converters
    import MySQLdb.cursors
except ImportError:
    # If MySQLdb isn't available this module won't actually be useable,
    # but we want it to at least be importable (mainly for readthedocs.org,
    # which has limitations on third-party modules)
    MySQLdb = None

import logger


version = "0.1"
version_info = (0, 1, 0, 0)

class _MysqlBase(object):
    """Torndb(tornado 使用的数据库引擎)的修改版，支持事务处理

    The main value we provide is wrapping rows in a dict/object so that
    columns can be accessed by name. Typical usage::

        db = database.Connection("localhost", "mydatabase")
        for article in db.query("SELECT * FROM articles"):
            print article.title

    Cursors are hidden by the implementation, but other than that, the methods
    are very similar to the DB-API.

    We explicitly set the timezone to UTC and the character encoding to
    UTF-8 on all connections to avoid time zone and encoding errors.
    """
    def __init__(self, host, database, user=None, password=None,
                 max_idle_time=7 * 3600):
        self.host = host
        self.database = database
        self.max_idle_time = max_idle_time

        args = dict(conv=CONVERSIONS, use_unicode=True, charset="utf8",
                    db=database, 
                    # init_command='SET time_zone = "+0:00"',
                    sql_mode="TRADITIONAL")
        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 3306

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception, e:
            if logger.CommonLog:
                logger.CommonLog.write('Cannot Connect to MySQL', e)
            raise

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = MySQLdb.connect(**self._db_args)
        self._db.autocommit(False)

    def commit(self):
        """提交事务
        """
        if getattr(self, "_db", None) is not None:
            self._db.commit()
            self.close()

    def rollback(self):
        """
        """
        if getattr(self, "_db", None) is not None:
            self._db.rollback()
            self.close()

    def iter(self, query, *parameters):
        """Returns an iterator for the given query and parameters."""
        self._ensure_connected()
        cursor = MySQLdb.cursors.SSCursor(self._db)
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(column_names, row))
        except:
            self.close()
            raise
        # finally:
        #     cursor.close()

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(itertools.izip(column_names, row)) for row in cursor]
        except:
            self.close()
            raise
        # finally:
        #     cursor.close()

    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    # rowcount is a more reasonable default return value than lastrowid,
    # but for historical compatibility execute() must return lastrowid.
    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        return self.execute_lastrowid(query, *parameters)

    def execute_lastrowid(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        except:
            self.close()
            raise
        # finally:
        #     cursor.close()

    def execute_rowcount(self, query, *parameters):
        """Executes the given query, returning the rowcount from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.rowcount
        except:
            self.close()
            raise
        # finally:
        #     cursor.close()

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        except:
            self.close()
            raise
        # finally:
        #     cursor.close()

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        except:
            self.close()
            raise
        # finally:
            # cursor.close()

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters):
        try:
            return cursor.execute(query, parameters)
        except OperationalError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.close()
            raise

    def format_query_param(self, query, parameters):
        param_str_pattern = '@\\w+'
        p_pattern = '%'
        match_all_param = re.findall(param_str_pattern, query)  # is an array
        if match_all_param:
            if parameters:
                query_result = ''
                parameter_array = []
                query_result = re.sub(p_pattern, '%%', query)
                query_result = re.sub(param_str_pattern, '%s', query_result)
                for each_param in match_all_param:
                    parameter_array.append(parameters[each_param])
                return query_result, parameter_array
            else:
                raise Exception("Not enough parameters to query")
        else:
            return query, parameters


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

if MySQLdb is not None:
    # Fix the access conversions to properly recognize unicode/binary
    FIELD_TYPE = MySQLdb.constants.FIELD_TYPE
    FLAG = MySQLdb.constants.FLAG
    CONVERSIONS = copy.copy(MySQLdb.converters.conversions)

    field_types = [FIELD_TYPE.BLOB, FIELD_TYPE.STRING, FIELD_TYPE.VAR_STRING]
    if 'VARCHAR' in vars(FIELD_TYPE):
        field_types.append(FIELD_TYPE.VARCHAR)

    for field_type in field_types:
        CONVERSIONS[field_type] = [(FLAG.BINARY, str)] + CONVERSIONS[field_type]

    # Alias some common MySQL exceptions
    IntegrityError = MySQLdb.IntegrityError
    OperationalError = MySQLdb.OperationalError


# 兼容旧版
MysqlTransaction = _MysqlBase


class MysqlConnection(_MysqlBase):
    """Mysql连接类，对_MysqlBase进行简单封装，增加对with语句的支持，旧版
    """
    def __init__(self, currentDBSetting):
        try:
            # currentDBSetting = config.GLOBAL_SETTINGS['db']
            _MysqlBase.__init__(self, currentDBSetting['host'],currentDBSetting['name'],
                                                      currentDBSetting['user'],currentDBSetting['psw'])
        except Exception, e:
            # print 'Mysql error %s'%str(e)
            raise

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # self.commit()
        self.close()

    def escape_str(self, instr):
        return MySQLdb.escape_string(instr)


# 以下为新版（>=1.0.13）接口

class MySQLConnection(_MysqlBase):
    """Mysql连接类，对_MysqlBase进行简单封装，增加对with语句的支持，自动提交
    """
    def __init__(self, currentDBSetting):
        try:
            # currentDBSetting = config.GLOBAL_SETTINGS['db']
            _MysqlBase.__init__(self, currentDBSetting['host'],currentDBSetting['name'],
                                                      currentDBSetting['user'],currentDBSetting['psw'])
        except Exception, e:
            # print 'Mysql error %s'%str(e)
            raise

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.commit()
        self.close()

    def escape_str(self, instr):
        return MySQLdb.escape_string(instr)

    def query(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.query(self, query_result, *parameters_new)

    def get(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.get(self, query_result, *parameters_new)

    def execute(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.execute(self, query_result, *parameters_new)

    def execute_lastrowid(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.execute_lastrowid(self, query_result, *parameters_new)

    def execute_rowcount(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.execute_rowcount(self, query_result, *parameters_new)



class MySQLTransaction(_MysqlBase):
    """Mysql连接类，对_MysqlBase进行简单封装，增加对with语句的支持，不自动提交
    """
    def __init__(self, currentDBSetting):
        try:
            # currentDBSetting = config.GLOBAL_SETTINGS['db']
            _MysqlBase.__init__(self, currentDBSetting['host'],currentDBSetting['name'],
                                                      currentDBSetting['user'],currentDBSetting['psw'])
        except Exception, e:
            # print 'Mysql error %s'%str(e)
            raise

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def escape_str(self, instr):
        return MySQLdb.escape_string(instr)

    def query(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.query(self, query_result, *parameters_new)

    def get(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.get(self, query_result, *parameters_new)

    def execute(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.execute(self, query_result, *parameters_new)

    def execute_lastrowid(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.execute_lastrowid(self, query_result, *parameters_new)

    def execute_rowcount(self, query, parameters):
        query_result, parameters_new = self.format_query_param(query, parameters)
        return _MysqlBase.execute_rowcount(self, query_result, *parameters_new)