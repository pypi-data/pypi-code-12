from __future__ import absolute_import

from turbodbc_intern import connect as intern_connect

from .exceptions import translate_exceptions
from .connection import Connection

def _make_connection_string(dsn, **kwargs):
    if dsn:
        kwargs['dsn'] = dsn
    return ';'.join(["{}={}".format(key, value) for key, value in kwargs.iteritems()])


@translate_exceptions
def connect(dsn=None, rows_to_buffer=None, parameter_sets_to_buffer=None, **kwargs):
    """
    Create a connection with the database identified by the dsn
    :param dsn: data source name as given in the odbc.ini file
    :param rows_to_buffer: Number of rows which shall be buffered
                           when result sets are fetched from the server.
                           None means that the default value is used.
    :param parameter_sets_to_buffer: Number of parameter sets (rows) which
                           shall be buffered when bulk queries are sent
                           to the server.
                           None means that the default value is used.
    :param \**kwargs: You may specify additional options as you please.
                      These options will go into the connection string.
                      Valid options depend on the specific database you
                      would like to connect with (e.g. `user` or `password`)
    """    
    connection = Connection(intern_connect(_make_connection_string(dsn, **kwargs)))

    if rows_to_buffer:
        connection.impl.rows_to_buffer = rows_to_buffer

    if parameter_sets_to_buffer:
        connection.impl.parameter_sets_to_buffer = parameter_sets_to_buffer

    return connection