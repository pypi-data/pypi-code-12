# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept the mysql-connector-python package.

"""

from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor


class MySQLConnectionInterceptor(DbAPIConnectionInterceptor):
    def get_backend_properties(self, conn, *args, **kwargs):
        return conn._host, conn._port, conn._database


class MySQLCursorInterceptor(DbAPICursorInterceptor):
    def get_connection(self, cursor):
        return cursor._connection


def intercept_mysql_connector_connection(agent, mod):
    MySQLConnectionInterceptor(agent, mod.MySQLConnection, MySQLCursorInterceptor, 'MYSQL').attach('_open_connection')
