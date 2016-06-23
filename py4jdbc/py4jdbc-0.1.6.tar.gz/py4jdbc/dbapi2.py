import re
import logging

from functools import partial

from py4jdbc.utils import CachedAttr
from py4jdbc.resultset import ResultSet, ColumnResultSet
from py4jdbc.gateway_process import GatewayProcess
from py4jdbc.exceptions import dbapi2 as dbapi2_exc
from py4jdbc.exceptions.py4j import reraise_jvm_exception


paramstyle = 'qmark'

# DB-API 2.0 Module Interface connect constructor
def connect(jdbc_url, user=None, password=None, gateway=None):
    return Connection(jdbc_url, user, password, gateway)


class _ExceptionMixin:
    '''Exposes dbapi2 exceptions classes as class-level attributes.
    '''
    Error = dbapi2_exc.Error
    Warning = dbapi2_exc.Warning
    InterfaceError = dbapi2_exc.InterfaceError
    DatabaseError = dbapi2_exc.DatabaseError
    InternalError = dbapi2_exc.InternalError
    OperationalError = dbapi2_exc.OperationalError
    ProgrammingError = dbapi2_exc.ProgrammingError
    IntegrityError = dbapi2_exc.IntegrityError
    DataError = dbapi2_exc.DataError
    NotSupportedError = dbapi2_exc.NotSupportedError


class _JdbcPropertyAlias:

    def __init__(self, property_name):
        self.name = property_name

    def __get__(self, inst, Cls):
        return inst.get_property(self.name)

    def __set__(self, inst, value):
        inst.set_property(self.name, value)


# DB-API 2.0 Connection Object
class Connection(_ExceptionMixin):

    autocommit = _JdbcPropertyAlias('AutoCommit')

    def __init__(self, jdbc_url, user=None, password=None, gateway=None, autocommit=None):
        self._gateway_arg = gateway
        self._jdbc_url = jdbc_url
        self._user = user
        self._password = password
        self._closed = False
        self._logger = logging.getLogger('py4jdbc')
        self._autostarted_gateway = False

        # Set autocommit
        if autocommit is not None:
            self.autocommit = autocommit

    def __enter__(self):
        if not self._gateway.is_running:
            self._gateway.run()
            self._autostarted_gateway = True
        return self

    def __exit__(self, *args):
        if not self._closed:
            self.close()
        # If this connection started a gateway server, shut it down now.
        if self._gateway.is_running and self._autostarted_gateway:
            msg = "Shutting down GatewayProcess auto-started by connection %r"
            self._logger.info(msg, self)
            self._gateway.shutdown()
        else:
            msg = ("GatewayProcess wasn't auto-started by connection. "
                   "Leaving it up.")
            self._logger.info(msg)

    # -----------------------------------------------------------------------
    # Py4j accessors.
    # -----------------------------------------------------------------------
    @property
    def _entry_point(self):
        return self._gateway.entry_point

    _ep = _entry_point

    @CachedAttr
    def _gateway_process(self):
        proc = GatewayProcess(require_ctx_manager=False)
        return proc

    @CachedAttr
    def _gateway(self):
        gw = self._gateway_arg
        if gw is not None:
            # If a gateway process was passed in, get the actual gateway.
            if isinstance(gw, GatewayProcess):
                gw = self._gateway_arg.gateway
            self._gateway = gw
            return gw
        return self._gateway_process.gateway

    # -----------------------------------------------------------------------
    # Java connection accessors.
    # -----------------------------------------------------------------------
    def get_property(self, name: str):
        method_name = 'get' + name
        if hasattr(self._jconn, method_name):
            method = getattr(self._jconn, method_name)
        else:
            method = partial(self._jconn.getProperty, name)
        with reraise_jvm_exception(self._gateway):
            return method()

    def set_property(self, name: str, value: str):
        method_name = 'set' + name
        if hasattr(self._jconn, method_name):
            method = getattr(self._jconn, method_name)
        else:
            method = partial(self._jconn.setProperty, name)
        with reraise_jvm_exception(self._gateway):
            return method(value)

    @CachedAttr
    def _py4jdbc_connection(self):
        self._logger.debug('Connecting as: %r', self._user, self._jdbc_url)
        return self._ep.getConnection(self._jdbc_url, self._user, self._password)

    @property
    def _conn(self):
        return self._py4jdbc_connection

    @CachedAttr
    def _jdbc_connection(self):
        return self._py4jdbc_connection.getJdbcConnection()

    @property
    def _jconn(self):
        return self._jdbc_connection

    def close(self):
        if self._closed:
            raise self.Error("Connection is already closed.")
        with reraise_jvm_exception(self._gateway):
            self._jconn.close()
            self._closed = True

    def commit(self):
        with reraise_jvm_exception(self._gateway):
            self._jconn.commit()

    def rollback(self):
        with reraise_jvm_exception(self._gateway):
            self._jconn.rollback()

    def cursor(self):
        return Cursor(self)

    # ------------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------------
    @CachedAttr
    def _metadata(self):
        return self._jdbc_connection.getMetaData()

    def get_tables(self, catalog=None, schema=None, table='%'):
        rs = self._metadata.getTables(catalog, schema, table, None)
        rs = self._ep.mkPyResultSet(rs)
        return ResultSet(rs, gateway=self._gateway, case_insensitive=True)

    def get_columns(self, catalog=None, schema=None, table='%', column=None):
        rs = self._metadata.getColumns(catalog, schema, table, column)
        rs = self._ep.mkPyResultSet(rs)
        return ColumnResultSet(rs, gateway=self._gateway)

    def get_primary_keys(self, catalog=None, schema=None, table='%', column=None):
        rs = self._metadata.getPrimaryKeys(catalog, schema, table)
        rs = self._ep.mkPyResultSet(rs)
        return ColumnResultSet(rs, gateway=self._gateway)

    def get_imported_keys(self, catalog=None, schema=None, table='%', column=None):
        rs = self._metadata.getImportedKeys(catalog, schema, table)
        rs = self._ep.mkPyResultSet(rs)
        return ColumnResultSet(rs, gateway=self._gateway)

    def get_exported_keys(self, catalog=None, schema=None, table='%', column=None):
        rs = self._metadata.getExportedKeys(catalog, schema, table)
        rs = self._ep.mkPyResultSet(rs)
        return ColumnResultSet(rs, gateway=self._gateway)


# DB-API 2.0 Cursor Object
class Cursor(_ExceptionMixin):

    def __init__(self, connection):
        self.connection = connection
        self._reset()
        self._logger = logging.getLogger('py4jdbc')

    def _reset(self):
        self._closed = False
        self._rs = None
        self._description = None

    # ------------------------------------------------------------------------
    # Shortcuts for reaching java objects.
    # ------------------------------------------------------------------------
    @property
    def _gateway(self):
        return self.connection._gateway

    @property
    def _entrypoint(self):
        return self.connection._entry_point

    _ep = _entrypoint

    @property
    def _jdbc_connection(self):
        return self.connection._jdbc_connection

    _jconn = _jdbc_connection

    # ------------------------------------------------------------------------
    # Actual dbapi 2.0 methods.
    # ------------------------------------------------------------------------
    @property
    def description(self):
        if self._description is None:
            self._description = self._rs.description()
        return self._description

    def close(self):
        if self._closed:
            raise self.Error("Connection is already closed.")
        self._logger.info('Closing cursor')
        self._close_last()
        self._closed = True

    def _close_last(self):
        if self._rs is not None:
            with reraise_jvm_exception(self._gateway):
                self._rs.close()

    def execute(self, operation, parameters=None):
        if self._closed:
            raise self.Error("Connection is closed.")
        with reraise_jvm_exception(self._gateway):
            if parameters is None:
                rs = self.connection._conn.execute(operation)
            else:
                rs = self.connection._conn.execute(operation, parameters)
            if rs is None:
                del self._rs
                return
            self._rs = ResultSet(rs, gateway=self._gateway)
            return self._rs

    def executemany(self, operation, parameter_seq):
        if self._closed:
            raise self.Error("Connection is closed.")
        with reraise_jvm_exception(self._gateway):
            rs = self.connection._conn.executeMany(operation, parameter_seq)
            if rs is None:
                del self._rs
                return
            self._rs = ResultSet(rs, gateway=self._gateway)
            return self._rs

    def fetchone(self):
        if self._closed:
            raise self.Error("Connection is closed.")
        return self._rs.fetchone()

    def fetchmany(self, size=None):
        if self._closed:
            raise self.Error("Connection is closed.")
        return self._rs.fetchmany(size)

    def fetchall(self):
        if self._closed:
            raise self.Error("Connection is closed.")
        return self._rs.fetchall()
