from django_cassandra_engine.utils import get_cassandra_connections
from .base import Model

for _, conn in get_cassandra_connections():
    conn.connect()
