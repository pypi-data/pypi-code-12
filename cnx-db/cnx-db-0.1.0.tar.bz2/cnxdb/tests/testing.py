# -*- coding: utf-8 -*-
import functools
import os
import sys

import psycopg2


_DEFAULT_CONNECTION_SETTINGS = {
    'dbname': 'testing',
    'user': 'tester',
    'password': 'tester',
    'host': 'localhost',
    'port': '5432',
    }
_DEFAULT_CONNECTION_STRING = ' '.join(
    ['{}={}'.format(key, value)
     for key, value in _DEFAULT_CONNECTION_SETTINGS.items()])
_CONNECTION_STRING = os.environ.get('TESTING_CONNECTION_STRING',
                                    _DEFAULT_CONNECTION_STRING)


def get_connection_string():
    """Retrieves the connection string from configuration."""
    return _CONNECTION_STRING


def db_connection_factory(connection_string=None):
    if connection_string is None:
        connection_string = get_connection_string()

    def db_connect():
        return psycopg2.connect(connection_string)

    return db_connect


def db_connect(method):
    """Decorator for methods that need to use the database

    Example:
    @db_connect
    def setUp(self, cursor):
        cursor.execute(some_sql)
        # some other code
    """
    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        connect = db_connection_factory()
        with connect() as db_connection:
            with db_connection.cursor() as cursor:
                return method(self, cursor, *args, **kwargs)
    return wrapped


def is_venv():
    """Returns a boolean telling whether the application is running
    within a virtualenv (aka venv).

    """
    return hasattr(sys, 'real_prefix')


__all__ = (
    'db_connect',
    'db_connection_factory',
    'get_connection_string',
    'is_venv',
    )
