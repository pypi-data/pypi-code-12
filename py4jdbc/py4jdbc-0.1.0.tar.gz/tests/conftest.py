import pytest

from py4jdbc.dbapi2 import Connection
from py4jdbc.gateway_process import GatewayProcess


@pytest.fixture(scope='session')
def gateway(request):
    gateway = GatewayProcess()
    gateway.__enter__()
    def finalizer():
        gateway.shutdown()
    request.addfinalizer(finalizer)
    return gateway


@pytest.fixture(scope='session')
def derby(request):
    # Start a gateway.
    gateway = GatewayProcess()
    gateway.__enter__()

    # Start a derby in-memory connection.
    url = "jdbc:derby:memory:testdb;create=true"
    conn = Connection(url, gateway=gateway)
    conn.__enter__()

    def finalizer():
        conn.__exit__()
        gateway.shutdown()
    request.addfinalizer(finalizer)

    return conn



