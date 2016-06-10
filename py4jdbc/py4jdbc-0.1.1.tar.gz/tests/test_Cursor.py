import pytest

from py4jdbc.dbapi2 import connect, Connection
from py4jdbc.resultset import ResultSet
from py4jdbc.exceptions.dbapi2 import Error


def test_connect(gateway):
    url = "jdbc:derby:memory:testdb;create=true"
    conn = connect(url, gateway=gateway)
    cur = conn.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert isinstance(rs, ResultSet)

def test_execute(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert isinstance(rs, ResultSet)


def test_fetchone(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert isinstance(rs.fetchone(), rs.Row)


def test_fetchmany(derby):
    '''Assert all rows of result set have the correct class.
    '''
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert all({isinstance(row, rs.Row) for row in rs.fetchmany(5)})


def test_fetchall(derby):
    '''Assert all rows of result set have the correct class.
    '''
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert all({isinstance(row, rs.Row) for row in rs.fetchall()})


def test_Cursor__iter__(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    assert all({isinstance(row, rs.Row) for row in rs})


def test_Cursor__iter__(derby):
    cur = derby.cursor()
    rs = cur.execute("select * from SYS.SYSTABLES")
    # Exhaust all rows.
    list(rs)
    assert rs.fetchone() == None


def test_close_and_execute(derby):
    cur = derby.cursor()
    cur.close()
    with pytest.raises(Error):
        cur.execute("select * from SYS.SYSTABLES")


def test_close_and_fetchone(derby):
    cur = derby.cursor()
    cur.execute("select * from SYS.SYSTABLES")
    cur.close()
    with pytest.raises(Error):
        cur.fetchone()


def test_close_twice(derby):
    cur = derby.cursor()
    cur.close()
    with pytest.raises(Error):
        cur.close()


