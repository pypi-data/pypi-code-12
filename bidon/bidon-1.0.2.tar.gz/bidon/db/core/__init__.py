"""This module contains classes that are used to compose data access objects."""
from .data_access_core import DataAccessCoreBase, InjectedDataAccessCore, get_pg_core
from .data_access_core import get_pooled_pg_core, get_sqlite_core, get_mysql_core
from .sql_writer import SqlWriter
