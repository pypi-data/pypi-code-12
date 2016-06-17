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

# The connection.queries property takes the queries_log and converts
# it to a list before returning.  This means that you can't just keep
# a reference to the queries property and check it before and after;
# you need to access the property anew each time.  Using this function
# each time will get an up-to-date query list.
def get_queries(db_alias=None):
    if db_alias is None:
        return connection.queries
    else:
        return connections[db_alias].queries

@contextmanager
def show_queries(db_alias=None, sqlparse_character_limit=2048):
    old_debug_setting = settings.DEBUG
    try:
        settings.DEBUG = True
        # This call to reset_queries ensures that the query list is
        # empty before running the wrapped code, and stops the query
        # log from just getting bigger and bigger if this context
        # manager is used repeatedly.
        reset_queries()
        yield
        queries_after = get_queries(db_alias)[:]
        number_of_queries = len(queries_after)
        print("--===--")
        print("Number of queries: {n}".format(n=number_of_queries))
        for i, q in enumerate(queries_after):
            query_time = q['time']
            query_sql = q['sql']
            query_length = len(query_sql)
            print("  Query {i} (taking {t}): ".format(i=i, t=query_time))
            # Outputting the formatted query takes a very long time
            # for large queries (e.g. those that prefetch_related can
            # generate with "IN (... thousands of IDs ...)"), so only
            # pretty-print queries that are fairly short.
            if SQLPARSE_AVAILABLE and query_length <= sqlparse_character_limit:
                formatted = sqlparse.format(
                    query_sql, reindent=True, keyword_case='upper')
                print(indent(formatted, 4))
            else:
                print(indent(query_sql, 4))
        print("End of query output.")
    finally:
        settings.DEBUG = old_debug_setting
