import os
from .queries import GET_TABLE_SCHEMA
from . import TYPE_MAP, db_conn


class Scanner(object):

    def __init__(self, db_url):
        self.conn = db_conn(db_url)

    def get_table_schema(self, table_name):
        r = None
        try:
            with self.conn.cursor() as c:
                c.execute(GET_TABLE_SCHEMA, (table_name, ))
                r = c.fetchall()
        except Exception:
            pass
        return r

    def build_props(self, table_name):
        cols = self.get_table_schema(table_name)
        props = {}
        for col in cols:
            props[col[0]] = dict(type=TYPE_MAP[col[1]])
        return props
