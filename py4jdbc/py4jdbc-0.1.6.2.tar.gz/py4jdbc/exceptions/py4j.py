import re
import pickle
import functools
import contextlib

import py4j.protocol

from py4jdbc.utils import CachedAttr, resolve_name
from py4jdbc.exceptions.dbapi2 import DatabaseError


_java_error_type_map = {
    'org.postgresql': 'py4jdbc.exceptions.postgres',
    'com.vertica': 'py4jdbc.exceptions.vertica',
    'java.sql': 'py4jdbc.exceptions.sqlstate',
}


@contextlib.contextmanager
def reraise_jvm_exception(gateway_client):
    try:
        yield
    except py4j.protocol.Py4JJavaError as py4j_exc:
        jexc = get_jvm_exc_data(py4j_exc.java_exception, gateway_client)

        # Special handling only applies to java.sql.SQLException
        if not jexc.is_java_sql_error():
            raise py4j_exc

        # Now find the corresponding py4jdbc exception and raise that one
        # from the Py4j exception.
        raise jexc.get_py4jdbc_exception() from py4j_exc


def get_jvm_exc_data(java_exc, gateway_client):
    exc_data = gateway_client.entry_point.getExceptionData(java_exc)
    exc_data = pickle.loads(exc_data)
    return _JavaException(java_exc, *exc_data)


class _JavaException:

    def __init__(self, java_exc, msg, traceback, classlist):
        self.java_exc = java_exc
        self.msg = msg
        self.tb = traceback
        getclassname = lambda s: s.split()[1]
        self.classlist = tuple(list(map(getclassname, classlist)))

    def get_py4jdbc_exception(self):
        exc = self.ExceptionClass(self)
        return exc

    def is_java_sql_error(self):
        return 'java.sql.SQLException' in self.classlist

    def tb_stripped(self):
        _, tb = self.tb.split(':', 1)
        return tb.strip()

    @CachedAttr
    def sqlstate(self):
        return self.java_exc.getSQLState()

    @property
    def sqlstate_class(self):
        return self.sqlstate[:2]

    @CachedAttr
    def errorcode(self):
        return self.java_exc.getErrorCode()

    @CachedAttr
    def javalib(self):
        '''I.e., returns org.postgresql from org.postgresql.util.PSQLError
        '''
        return re.match(r'\w+\.\w+', self.classlist[0]).group()

    @CachedAttr
    def exc_messages(self):
        sqlstate_mod = 'py4jdbc.exceptions.sqlstate'
        exc_module = _java_error_type_map.get(self.javalib, sqlstate_mod)
        return resolve_name('messages', exc_module)

    @CachedAttr
    def exc_classes(self):
        exc_module = _java_error_type_map[self.javalib]
        return resolve_name('exc_classes', exc_module)

    @property
    def ExceptionClass(self):
        '''Retrieve a custom exception class, if any, otherwise
        return DatabaseError.
        '''
        return self.exc_classes.get(self.sqlstate_class, DatabaseError)

