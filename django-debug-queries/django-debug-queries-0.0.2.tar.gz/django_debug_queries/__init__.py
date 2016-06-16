from __future__ import print_function, unicode_literals

from contextlib import contextmanager
import re

from django.conf import settings
from django.db import connection, connections, reset_queries

try:
    import sqlparse
    SQLPARSE_AVAILABLE = True
except ImportError:
    SQLPARSE_AVAILABLE = False

def indent(s, n=2):
    spaces = ' ' * n
    return re.sub(r'(?ms)^', spaces, s)

@contextmanager
def show_queries(db_alias=None):
    if db_alias is None:
        queries = connection.queries
    else:
        queries = connections[db_alias].queries
    old_debug_setting = settings.DEBUG
    try:
        settings.DEBUG = True
        reset_queries()
        number_of_queries_before = len(queries)
        yield
        queries_after = queries[number_of_queries_before:]
        number_of_queries = len(queries_after) - number_of_queries_before
        print("--===--")
        print("Number of queries: {n}".format(n=number_of_queries))
        for i, q in enumerate(queries_after[number_of_queries_before:]):
            query_time = q['time']
            query_sql = q['sql']
            print("  Query {i} (taking {t}): ".format(i=i, t=query_time))
            if SQLPARSE_AVAILABLE:
                formatted = sqlparse.format(
                    query_sql, reindent=True, keyword_case='upper')
                print(indent(formatted, 4))
            else:
                print(indent(query_sql, 4))
    finally:
        settings.DEBUG = old_debug_setting
