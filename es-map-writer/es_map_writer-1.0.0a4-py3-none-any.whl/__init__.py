import os
import psycopg2
from urllib.parse import urlparse
from elasticsearch import Elasticsearch


APP_DIR = 'es_map_writer'


DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgres://postgres:postgres@{}:5432/postgres'.format(os.getenv('DB_1_PORT_5432_TCP_ADDR')))

ES_NODE_URL = os.getenv('ES_NODE_URL', '')
ES_NODE_PORT = int(os.getenv('ES_NODE_PORT', 9200))

TYPE_MAP = {  # Maps PostgreSQL data type keys to Elasticsearch data type vals
    'serial primary key': 'integer',
    'integer': 'integer',
    'character varying': 'string',
    'varchar': 'string',
    'character': 'string',
    'char': 'string',
    'text': 'string',
    'integer': 'integer',
    'timestamp with time zone': 'date',
    'timestamp': 'date',
    'date': 'date',
    'boolean': 'boolean',
    'bytea': 'binary',
    'jsonb': 'object',
    'json': 'object',
    'bigint': 'long',
    'smallint': 'integer',
    'decimal': 'float',
    'numeric': 'float',
    'real': 'integer',
    'double precision': 'double',
    'smallserial': 'integer',
    'serial': 'integer',
    'bigserial': 'long',
    'money': 'long',
}


MAPPING_TEMPLATE = """%(map_name)s_mapping = {
    "mappings": {
        "%(doc_type)s": {
            "properties": %(fields)s
        }
    }
}
"""


def db_conn(db_url):
    parts = urlparse(db_url)
    db = parts.path.strip('/')
    user = parts.username
    pw = parts.password
    port = parts.port
    host = parts.hostname
    connection = psycopg2.connect(
        host=host, port=port, user=user, password=pw, database=db)
    connection.set_session(autocommit=True)
    return connection


def es_conn():
    return Elasticsearch([{'host': ES_NODE_URL, 'port': ES_NODE_PORT}])
