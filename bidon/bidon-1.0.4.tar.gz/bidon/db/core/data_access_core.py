"""The data_access_core module contains the DataAccessCoreBase class and some useful derivations,
as well as methods for constructing cores for common database systems, including PostgreSQL, SQLite,
and MySQL.
"""
from .sql_writer import SqlWriter


__all__ = ["DataAccessCoreBase",
           "InjectedDataAccessCore",
           "get_pg_core",
           "get_pooled_pg_core",
           "get_sqlite_core",
           "get_mysql_core"]


SQL_CAST = "cast({0} as {1})"


class DataAccessCoreBase(object):
  """Contains settings for DataAccess that allows different database engines to be supported."""
  def __init__(self, sql_writer=("%({0})s", "%s", SQL_CAST), empty_params=None,
               supports_timezones=True, supports_returning_syntax=True):
    """Initialize a DataAccessCoreBase instance.

    :param sql_writer: either a SqlWriter instance or a tuple of constructor arguments.
    :param empty_params: the value that should be used when the params passed to exec are None
    :param supports_timezones: whether or not the database supports timezones in timestamps
    :type supports_timezones: boolean
    :param supports_returning_syntax: whether or not the database supports the returning syntax
    :type supports_returning_syntax: boolean
    """
    self.sql_writer = sql_writer if isinstance(sql_writer, SqlWriter) else SqlWriter(*sql_writer)
    self.empty_params = empty_params
    self.supports_timezones = supports_timezones
    self.supports_returning_syntax = supports_returning_syntax

  def open(self):
    """Open a connection.

    This is an abstract method.
    """
    raise NotImplementedError()

  def close(self, connection, *, commit=True):
    """Close a connection, commiting pending changes if commit is True.

    This is an abstract method.
    """
    raise NotImplementedError()

  def get_autocommit(self, connection):
    """Gets connection's autocommit value.

    This is an abstract method.
    """
    raise NotImplementedError()

  def set_autocommit(self, connection, value):
    """Sets connection's autocommit value.

    This is an abstract method.

    :param connection: a connection instance
    :param value: the value to set autocommit to
    """
    raise NotImplementedError()


class InjectedDataAccessCore(DataAccessCoreBase):
  """An implementation of DataAccessCoreBase where the open and close methods are passed to the
  constructor.
  """
  def __init__(self, opener, closer, sql_writer=("%({0})s", "%s", SQL_CAST), *, empty_params=None,
               supports_timezones=True, supports_returning_syntax=True, get_autocommit=None,
               set_autocommit=None):
    super().__init__(sql_writer, empty_params, supports_timezones, supports_returning_syntax)
    self.opener = opener
    self.closer = closer
    self._get_autocommit = get_autocommit
    self._set_autocommit = set_autocommit

  def open(self):
    """Open and return a connection using the opener method passed to the constructor."""
    return self.opener()

  def close(self, connection, *, commit=True):
    """Close the connection using the closer method passed to the constructor."""
    if commit:
      connection.commit()
    else:
      connection.rollback()
    self.closer(connection)

  def get_autocommit(self, connection):
    """Gets connection's autocommit value."""
    return self._get_autocommit(connection)

  def set_autocommit(self, connection, value):
    """Sets connection's autocommit value."""
    return self._set_autocommit(connection, value)


def default_connection_closer(connection):
  """The default connection closer complying with DB API 2.0 standards."""
  connection.close()


def get_pg_autocommit(cn):
  """PostgreSQL autocommit getter for core."""
  return cn.autocommit


def set_pg_autocommit(cn, autocommit):
  """PostgreSQL autocommit setter for core."""
  cn.autocommit = autocommit


def get_pg_core(connection_string, *, cursor_factory=None, edit_connection=None):
  """Creates a simple PostgreSQL core. Requires the psycopg2 library."""
  import psycopg2 as pq
  from psycopg2.extras import NamedTupleCursor

  def opener():
    """Opens a single PostgreSQL connection with the scope-captured connection string."""
    cn = pq.connect(connection_string)
    cn.cursor_factory = cursor_factory or NamedTupleCursor
    if edit_connection:
      edit_connection(cn)
    return cn

  return InjectedDataAccessCore(
    opener,
    default_connection_closer,
    ("%({0})s", "%s", "{0}::{1}"),
    empty_params=None,
    supports_timezones=True,
    supports_returning_syntax=True,
    get_autocommit=get_pg_autocommit,
    set_autocommit=set_pg_autocommit)


def get_pooled_pg_core(connection_string, pool_size=None, *, cursor_factory=None,
                       edit_connection=None, threaded=True):
  """Creates a pooled PostgreSQL core. Requires the psycopg2 library.

  :pool_size: must be a 2-tuple in the form (min_connections, max_connections).
  """
  from psycopg2.extras import NamedTupleCursor
  from psycopg2.pool import ThreadedConnectionPool as TPool, SimpleConnectionPool as SPool
  if not pool_size:
    pool_size = (5, 10)
  if threaded:
    pool = TPool(pool_size[0], pool_size[1], connection_string)
  else:
    pool = SPool(pool_size[0], pool_size[1], connection_string)

  def opener():
    """Gets a PostgreSQL connection from the scope-captured connection pool."""
    cn = pool.getconn()
    cn.cursor_factory = cursor_factory or NamedTupleCursor
    if edit_connection:
      edit_connection(cn)
    return cn

  def closer(connection):
    """Returns a connection to the scope-captured connection pool."""
    pool.putconn(connection)

  return InjectedDataAccessCore(
    opener,
    closer,
    ("%({0})s", "%s", "{0}::{1}"),
    empty_params=None,
    supports_timezones=True,
    supports_returning_syntax=True,
    get_autocommit=get_pg_autocommit,
    set_autocommit=set_pg_autocommit)


def get_sqlite_autocommit(cn):
  """SQLite autocommit getter for core."""
  return cn.isolation_level is None


def set_sqlite_autocommit(cn, autocommit):
  """SQLite autocommit setter for core."""
  if isinstance(autocommit, bool):
    cn.isolation_level = None if autocommit else ""
  else:
    cn.isolation_level = autocommit


def get_sqlite_core(connection_string, *, cursor_factory=None, edit_connection=None):
  """Creates a simple SQLite3 core."""
  import sqlite3 as sqlite

  def opener():
    """Opens a single connection with the scope-captured connection string."""
    cn = sqlite.connect(connection_string)
    if cursor_factory:
      cn.row_factory = cursor_factory
    if edit_connection:
      edit_connection(cn)
    return cn

  return InjectedDataAccessCore(
    opener,
    default_connection_closer, (":{0}", "?", SQL_CAST),
    empty_params=[],
    supports_timezones=True,
    supports_returning_syntax=False,
    get_autocommit=get_sqlite_autocommit,
    set_autocommit=set_sqlite_autocommit)


def get_mysql_autocommit(cn):
  """MySQL autocommit getter for core."""
  return cn.get_autocommit()


def set_mysql_autocommit(cn, autocommit):
  """MySQL autocommit setter for core."""
  cn.autocommit(autocommit)


def get_mysql_core(connection_args, *, cursor_factory=None, edit_connection=None):
  """Creates a simple MySQL core. Requires the pymysql library."""
  import pymysql

  def opener():
    """Opens a single connection with the scope-captured connection string."""
    cn = pymysql.connect(**connection_args)
    if cursor_factory:
      cn.cursorclass = cursor_factory
    if edit_connection:
      edit_connection(cn)
    return cn

  return InjectedDataAccessCore(
    opener,
    default_connection_closer,
    ("%({0})s", "%s", SQL_CAST),
    empty_params=None,
    supports_timezones=False,
    supports_returning_syntax=False,
    get_autocommit=get_mysql_autocommit,
    set_autocommit=set_mysql_autocommit)
