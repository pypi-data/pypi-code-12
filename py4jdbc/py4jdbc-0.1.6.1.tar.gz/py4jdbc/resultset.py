import io
import pickle
import logging
import collections

from py4jdbc.utils import CachedAttr
from py4jdbc.java_sql_types import java_sql_types
from py4jdbc.exceptions.py4j import reraise_jvm_exception


class ResultSet:

    def __init__(self, rs, gateway, batchsize=500,
                 fieldnames_attr='column_names', case_insensitive=False):
        self._gateway = gateway
        self._rs = rs
        self._fieldnames_attr = fieldnames_attr
        self._logger = logging.getLogger('py4jdbc')
        self._case_insensitive = case_insensitive
        self.index = 0
        self.batchsize = 500

    def metadata(self):
        '''Get all resultset metadata as a dictionary.
        '''
        meta = self._rs.getMetadataMap()
        return meta

    def close(self):
        self._logger.debug('Closing %r', self)
        self._rs.close()

    def _make_rows(self, bytes):
        values = pickle.loads(bytes)
        rows = tuple(map(self.Row._make, values))
        self.index += len(rows)
        return rows

    @CachedAttr
    def rows(self):
        return self.fetchall()

    @CachedAttr
    def column_names(self):
        self._logger.info('Fetching column names: %r', self)
        with reraise_jvm_exception(self._gateway):
            resp = self._rs.colNames()
        return pickle.loads(resp)

    @property
    def column_labels(self):
        self._logger.debug('Fetching column labels: %r', self)
        with reraise_jvm_exception(self._gateway):
            resp = self._rs.colLabels()
        return pickle.loads(resp)

    @CachedAttr
    def Row(self):
       field_names = getattr(self, self._fieldnames_attr)
       return make_row(field_names, case_insensitive=self._case_insensitive)

    def fetchone(self):
        self._logger.debug('Fetching one: %r', self)
        vals = pickle.loads(self._rs.fetchOne())
        if vals:
            return self.Row(*vals)

    def fetchmany(self, size=None):
        self._logger.debug("Batchsize is %d", size)
        with reraise_jvm_exception(self._gateway):
            resp = self._rs.fetchMany(size)
        return self._make_rows(resp)

    def fetchall(self):
        msg = ('Calling fetching all can cause memory errors '
               'in the py4jdbc gateway server. Consider using fetchmany '
               'instead.')
        self._logger.warning(msg)
        with reraise_jvm_exception(self._gateway):
            resp = self._rs.fetchAll()
        return self._make_rows(resp)

    def description(self):
        self._logger.debug('Getting cursor description.')
        with reraise_jvm_exception(self._gateway):
            resp = self._rs.getDescription()
        return pickle.loads(resp)

    def next(self):
        return self.fetchone()

    def __iter__(self):
        self._logger.debug('Iterating over result set: %r', self)
        while True:
            batch = self.fetchmany(self.batchsize)
            if not batch:
                self._logger.debug('Done iterating over result set: %r', self)
                return
            for row in batch:
                yield row


class ColumnResultSet(ResultSet):

    _type_map = dict(item[::-1] for item in java_sql_types)

    @CachedAttr
    def Row(self):
        field_names = getattr(self, self._fieldnames_attr)
        BaseRow = make_row(field_names, case_insensitive=True)
        class ColumnRow(BaseRow):
            _type_map = self._type_map
            @property
            def data_type(self):
                return self._type_map[self.DATA_TYPE]
        return ColumnRow

# ------------------------------------------------------------------------------
# Row base class.
# ------------------------------------------------------------------------------
class _RowFieldAccessor:
    '''Used to lokup values in the row tuple.
    '''
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __get__(self, inst, Cls=None):
        idx = inst._fieldnames.index(self.fieldname)
        return inst[idx]

    __getitem__ = object.__getattribute__


class _Row(tuple):
    '''A modified namedtuple supports dict-style value access and doesn't
    mangle field names or complain about fieldnames that clash with Python
    keywords. Subclasses must supply _fieldnames and __slots__
    '''
    _fieldnames = None
    __slots__ = tuple()

    def __new__(Cls, *values):
        return tuple.__new__(Cls, values)

    @classmethod
    def _make(Cls, iterable):
        return tuple.__new__(Cls, iterable)

    def _replace(self, **kwds):
        'Return a new a object replacing specified fields with new values'
        result = self._make(map(kwds.pop, self._fieldnames, _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % list(kwds))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return '%s(%r)' % (self.__class__.__name__, self._asdict())

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values.'
        return collections.OrderedDict(zip(self._fieldnames, self))

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)


def make_row(fieldnames, case_insensitive=False):
    '''Return a customized namedtuple variant that supports lower-case
    access of all values by column name.
    '''
    flds = tuple(fieldnames)
    lc_flds = tuple(s.lower() for s in flds)
    slots = _Row.__slots__ + flds + lc_flds

    members = [('_fieldnames', flds)]
    for field in flds:
        members.append((field, _RowFieldAccessor(field)))
        # This effectively makes lookups case-insensitive.
        if case_insensitive:
            members.append((field.lower(), _RowFieldAccessor(field)))

    Row = type('Row', (_Row,), dict(members))

    return Row


# class ResultSetMeta:

#     def __init__(self, meta):
#         self._meta = meta

#     @property
#     def column_no_nulls(self):
#         '''The constant indicating that a column does not allow NULL value
#         '''
#         return self._meta.columnNoNulls()

#     @property
#     def column_nullable(self):
#         '''The constant indicating that a column allows NULL value
#         '''
#         return self._meta.columnNullable()

#     @property
#     def column_nullable_unknown(self):
#         ''' indicating that the nullability of a column's values is unknown.
#         '''
#         return self._meta.columnNullableUnknown()

#     def get_catalog_name(self, column):
#         '''Gets the designated column's table's catalog name.
#         '''
#         return self._meta.getCatalogName(column)

#     def get_column_class_name(self, column):
#         '''Returns the fully-qualified name of the Java class whose instances
#         are manufactured if the method ResultSet.getObject is called to
#         retrieve a value from the column.'''
#         return self._meta.getColumnClassName(column)

#     def get_column_count(self):
#         '''Returns the number of columns in this ResultSet object.
#         '''
#         return self._meta.getColumnCount()

#     def get_column_display_size(self, column):
#         '''Indicates the designated column's normal maximum width in
#         characters.
#         '''
#         return self._meta.getColumnDisplaySize(column)

#     def get_column_label(self, column):
#         '''Gets the designated column's suggested title for use in printouts
#         and displays.
#         '''
#         return self._meta.getColumnLabel(column)

#     def get_column_name(self, column):
#         '''Get the designated column's name.
#         '''

#         return self._meta.getColumnName(column)

#     def get_column_type(self, column):
#         '''Retrieves the designated column's SQL type.
#         '''
#         return self._meta.getColumnType(column)

#     def get_column_type_name(self, column):
#         '''Retrieves the designated column's database-specific type name.
#         '''
#         return self._meta.getColumnTypeName(column)

#     def get_precision(self, column):
#         '''Get the designated column's specified column size.
#         '''
#         return self._meta.getPrecision(column)

#     def get_scale(self, column):
#         '''Gets the designated column's number of digits to right of the
#         decimal point.
#         '''
#         return self._meta.getScale(column)

#     def get_schema_name(self, column):
#         '''Get the designated column's table's schema.
#         '''
#         return self._meta.getSchemaName(column)

#     def get_table_name(self, column):
#         '''Gets the designated column's table name.
#         '''
#         return self._meta.getTableName(column)

#     def is_auto_increment(self, column):
#         '''Indicates whether the designated column is automatically numbered.
#         '''
#         return self._meta.isAutoIncrement(column)

#     def is_case_sensitive(self, column):
#         '''Indicates whether a column's case matters.
#         '''

#         return self._meta.isCaseSensitive(column)

#     def is_currency(self, column):
#         '''Indicates whether the designated column is a cash value.
#         '''
#         return self._meta.isCurrency(column)

#     def is_definitely_writable(self, column):
#         '''Indicates whether a write on the designated column will definitely
#         succeed.
#         '''
#         return self._meta.isDefinitelyWritable(column)

#     def is_nullable(self, column):
#         '''Indicates the nullability of values in the designated column.
#         '''
#         return self._meta.isNullable(column)

#     def is_read_only(self, column):(column)
#         '''Indicates whether the designated column is definitely not writable.
#         '''
#         return self._meta.isReadOnly(column)

#     def is_searchable(self, column):
#         '''Indicates whether the designated column can be used in a where
#         clause.
#         '''
#         return self._meta.isSearchable(column)

#     def is_signed(self, column):
#         '''Indicates whether values in the designated column are signed
#         numbers.
#         '''
#         return self._meta.isSigned(column)

#     def is_writable(self, column):
#         '''Indicates whether it is possible for a write on the designated
#         column to succeed.
#         '''
#         return self._meta.isWritable(column)
