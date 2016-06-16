from __future__ import print_function, unicode_literals

from contextlib import contextmanager
import re

from django.conf import settings
from django.db import connection, reset_queries

def indent(s, n=2):
    spaces = ' ' * n
    return re.sub(r'(?ms)^', spaces, s)

@contextmanager
def show_queries(db_alias=None):
    old_debug_setting = settings.DEBUG
    try:
        settings.DEBUG = True
        reset_queries()
        number_of_queries_before = len(connection.queries)
        yield
        queries_after = connection.queries[number_of_queries_before:]
        number_of_queries = len(queries_after) - number_of_queries_before
        print("--===--")
        print("Number of queries: {n}".format(n=number_of_queries))
        for i, q in enumerate(queries_after[number_of_queries_before:]):
            query_time = q['time']
            query_sql = q['sql']
            print("  Query {i} (taking {t}): ".format(i=i, t=query_time))
            try:
                import sqlparse
                formatted = sqlparse.format(
                    query_sql, reindent=True, keyword_case='upper')
                print(indent(formatted, 4))
            except ImportError:
                print(indent(query_sql, 4))
    finally:
        settings.DEBUG = old_debug_setting
