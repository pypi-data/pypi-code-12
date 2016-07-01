# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept the MySQLdb package.

"""

from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor


class MySQLdbConnectionInterceptor(DbAPIConnectionInterceptor):
    def get_backend_properties(self, conn, *args, **kwargs):
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', '3306')
        db = kwargs.get('database', kwargs.get('db', ''))
        return host, port, db


class MySQLdbCursorInterceptor(DbAPICursorInterceptor):
    def get_connection(self, cursor):
        return cursor.connection


def intercept_MySQLdb_connection(agent, mod):
    MySQLdbConnectionInterceptor(agent, mod.Connection, MySQLdbCursorInterceptor, 'MYSQL').attach('__init__')
