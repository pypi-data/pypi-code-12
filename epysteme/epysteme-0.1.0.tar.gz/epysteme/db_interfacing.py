# -*- coding: utf-8 -*-
"""Database interfacing classes and functions for epysteme

This module contains the Database class and various functions related to it

Author: Stefan Peterson
"""

try:
    import pymssql
    from _pymssql_methods import (ms_cc_tuple,
                                  ms_get_something)
    mssql_available = True
except ImportError:
    mssql_available = False

try:
    import pymysql
    from _pymysql_methods import (my_cc_tuple,
                                  my_get_something)
    mysql_available = True
except ImportError:
    mysql_available = False

from _sqlite_methods import (lite_cc_tuple,
                             lite_get_something)


class Database(object):

    def __init__(self, db_type, *args):
        # Dynamically define methods based on database type
        method_names = ("make_cc_tuple",
                        "get_something")

        if db_type.upper() in ("MS", "MSSQL"):
            if not mssql_available:
                raise ImportError("pymssql not available")
            methods = (ms_cc_tuple,
                       ms_get_something)

        elif db_type.upper() == "MYSQL":
            if not mysql_available:
                raise ImportError("pymysql not available")
            methods = (my_cc_tuple,
                       my_get_something)

        elif db_type.upper() in ("SQLITE", "SQLITE3"):
            methods = (lite_cc_tuple,
                       lite_get_something)

        else:
            raise ValueError("Database type '%s' is not supported" % db_type)

        for method_name, method in zip(method_names, methods)
            setattr(self, method_name, method)