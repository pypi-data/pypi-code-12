from py4jdbc.dbapi2 import *
from py4jdbc.exceptions.dbapi2 import *


py4jdbc_connect = connect

# DB-API 2.0 Module Interface connect constructor
def connect(host, port=None, database=None, user=None, password=None, gateway=None):
    if port is not None:
        jdbc_url = 'jdbc:vertica://%s:%s/%s' % (host, port, database)
    else:
        jdbc_url = 'jdbc:vertica://%s/%s'
        jdbc_url = jdbc_url % (host, database)
    return py4jdbc_connect(jdbc_url, user, password, gateway)

