import psycopg2
from .base import BaseAdapter


class Adapter(BaseAdapter):

    @property
    def _client(self):
        uri = self._uri
        conn = psycopg2.connect(
            host=uri.host,
            user=uri.username,
            password=uri.password,
            database=uri.database,
            port=uri.port
        )
        conn.autocommit = True
        return conn

    def _ensure_db_has_migration_table(self):
        cursor = self._client.cursor()
        cursor.execute("""
        SELECT EXISTS( SELECT 1 FROM information_schema.tables WHERE
        table_schema = 'public' AND table_name = {placeholder});
        """.format(
            placeholder=self.placeholder
        ), [self.table_name])
        table_exists = bool(cursor.fetchone()[0])
        if not table_exists:
            self.create_table_for_migrations()

    def create_table_for_migrations(self):
        cursor = self._client.cursor()
        table_sql = """
        CREATE TABLE {} (
        id serial,
        name varchar(100) not null default '',
        applied_at timestamp not null default CURRENT_TIMESTAMP,
        package varchar(20) not null default 'main',
        PRIMARY KEY (id)
        )
        """.format(self.table_name)
        cursor.execute(table_sql)
