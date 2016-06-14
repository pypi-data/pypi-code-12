import pytest

from py4jdbc.dbapi2 import Connection
from py4jdbc.exceptions import dbapi2
from py4jdbc.exceptions import sqlstate


def test_jdbc_bogus_driver(gateway):
    url = "jdbc:darby:memory:testdb;create=true"
    conn = Connection(url, gateway=gateway)
    with pytest.raises(sqlstate.ConnectionError), conn:
        cur = derby.cursor()
        rs = cur.execute("select * from SYS.SYSTABLES")


def test_jdbc_bogus_table(derby):
    cur = derby.cursor()
    with pytest.raises(sqlstate.SyntaxOrAccessRuleViolationError):
        rs = cur.execute("select * from BOGUS_TABLE")

