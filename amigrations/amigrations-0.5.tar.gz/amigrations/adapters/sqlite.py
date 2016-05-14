import time
import sqlite3
from .base import BaseAdapter


class Adapter(BaseAdapter):

    placeholder = '?'

    @property
    def _client(self):
        uri = self._uri
        conn = sqlite3.connect(uri.database)
        conn.isolation_level = None
        return conn

    def _ensure_db_has_migration_table(self):
        cursor = self._client.cursor()
        cursor.execute("""
        SELECT count(*) FROM sqlite_master WHERE type='table'
         AND name={placeholder};
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
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name varchar(100) not null default '',
        applied_at timestamp not null default CURRENT_TIMESTAMP,
        package varchar(20) not null default 'main'
        )
        """.format(self.table_name)
        cursor.execute(table_sql)

    def transform_datetime_into_sql_format(self, datetime_val):
        return time.mktime(datetime_val.timetuple())
