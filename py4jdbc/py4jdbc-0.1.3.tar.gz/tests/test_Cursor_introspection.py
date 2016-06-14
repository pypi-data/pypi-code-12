import pytest

from py4jdbc.dbapi2 import connect, Connection
from py4jdbc.resultset import ResultSet
from py4jdbc.exceptions.dbapi2 import Error


def test_get_tables(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    sql_names = [row.TABLENAME for row in rs]
    jdbc_names = [row.TABLE_NAME for row in derby.get_tables()]
    assert set(sql_names) == set(jdbc_names)


def test_get_columns(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSCOLUMNS")
    sql_names = [row.COLUMNNAME for row in rs]
    jdbc_names = [row.COLUMN_NAME for row in derby.get_columns()]
    assert  set(jdbc_names).issubset(set(sql_names))





