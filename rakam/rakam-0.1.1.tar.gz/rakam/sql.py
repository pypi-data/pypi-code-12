import pytz
from itertools import izip
from collections import OrderedDict
from six import string_types

from rakam.utils import parse_date, parse_time, parse_datetime
from rakam.exceptions import BadSqlResponse, SqlRequestFailed, \
    BadSqlMetadata, BadSqlResult


def _parse_date(val):
    return parse_date(val)


def _parse_time(val):
    return parse_time(val)


def _parse_datetime(val):
    return parse_datetime(val).astimezone(pytz.utc)


class RakamFieldMeta(object):
    RAKAM_FIELD_SERIALIZERS = {
        'STRING': unicode,
        'INTEGER': int,
        'DECIMAL': float,
        'DOUBLE': float,
        'LONG': long,
        'BOOLEAN': bool,
        'DATE': _parse_date,
        'TIME': _parse_time,
        'TIMESTAMP': _parse_datetime,
        'ARRAY_STRING': lambda col: map(unicode, col),
        'ARRAY_INTEGER': lambda col: map(int, col),
        'ARRAY_DECIMAL': lambda col: map(float, col),
        'ARRAY_DOUBLE': lambda col: map(float, col),
        'ARRAY_LONG': lambda col: map(long, col),
        'ARRAY_BOOLEAN': lambda col: map(bool, col),
        'ARRAY_DATE': lambda col: map(_parse_date, col),
        'ARRAY_TIME': lambda col: map(_parse_time, col),
        'ARRAY_TIMESTAMP': lambda col: map(_parse_datetime, col),
    }

    def __init__(self, name, _type, unique=False, descriptive_name='', description=None, category=None):
        self.name = name
        self.type = _type
        self.unique = unique
        self.descriptive_name = descriptive_name
        self.description = description
        self.category = category

        self.serializer = self._get_serializer()

    def _get_serializer(self):
        return self.RAKAM_FIELD_SERIALIZERS.get(self.type, lambda col: col)


class RakamSqlResult(object):
    def __init__(self, rows, metadata, properties=None):
        if properties is None:
            properties = {}

        self.rows = rows
        self.metadata = metadata
        self.properties = properties


class RakamSqlParser(object):
    iterable_types = (list, tuple)
    dict_types = (dict, OrderedDict)

    def parse(self, sql_result):
        failed = sql_result.get('failed', False)
        properties = sql_result.get('properties', None)
        result = sql_result.get('result', None)
        metadata = sql_result.get('metadata', None)
        error = sql_result.get('error', None)

        if failed:
            raise SqlRequestFailed("sql query failed. error: %s" % (error,))

        if properties is None:
            raise BadSqlResponse("properties is missing.")

        if not isinstance(properties, self.dict_types):
            raise BadSqlResponse("properties is must be dict. given: %s" % (type(properties),))

        if result is None:
            raise BadSqlResponse("result is missing.")

        if not isinstance(result, self.iterable_types):
            raise BadSqlResponse("result must be a list. given: %s", (type(result),))

        if metadata is None:
            raise BadSqlResponse("metadata is missing.")

        if not isinstance(metadata, self.iterable_types):
            raise BadSqlResponse("metadata must be a list. given: %s", (type(metadata),))

        field_metas = self._parse_metadata(metadata)
        rows = self._parse_rows(result, field_metas)
        return RakamSqlResult(rows, field_metas, properties=properties)

    def _parse_metadata(self, metadata_list):
        return map(self._parse_meta, metadata_list)

    def _parse_meta(self, meta_dict):
        name = meta_dict.get('name', None)
        _type = meta_dict.get('type', None)
        unique = meta_dict.get('unique', False)
        descriptive_name = meta_dict.get('descriptiveName', '')
        description = meta_dict.get('description', None)
        category = meta_dict.get('category')

        if name is None:
            raise BadSqlMetadata("name is missing.")

        if not isinstance(name, string_types):
            raise BadSqlMetadata("name must be a string. given: %s" % (type(name),))

        if _type is None:
            raise BadSqlMetadata("type is missing.")

        if not isinstance(_type, string_types):
            raise BadSqlMetadata("type must be a string. given: %s" % (type(_type),))

        return RakamFieldMeta(
            name, _type, unique=unique,
            descriptive_name=descriptive_name,
            description=description,
            category=category
        )

    def _parse_rows(self, rows_raw, field_metas):
        num_fields = len(field_metas)
        row_types = self.iterable_types

        rows = []
        for row_index, row_raw in enumerate(rows_raw):
            if not isinstance(row_raw, row_types):
                raise BadSqlResult("Invalid type for row at index: %s" % (row_index,))

            if len(row_raw) != num_fields:
                raise BadSqlResult("Invalid number of fields for row at index %s: %s" % (row_index, len(row_raw),))

            row = self._parse_row(row_raw, field_metas, row_index)
            rows.append(row)

        return rows

    def _parse_row(self, row_raw, field_metas, row_index):
        parse_column = self._parse_column
        row = tuple(
            parse_column(col, field_meta, row_index, col_index)
            for col, field_meta, col_index
            in izip(row_raw, field_metas, xrange(len(row_raw)))
        )

        return row

    def _parse_column(self, col_raw, field_meta, row_index, col_index):
        if col_raw is not None:
            try:
                return field_meta.serializer(col_raw)
            except Exception as exc:
                raise BadSqlResult("Invalid value at row: %s column: %s error: %s" % (row_index, col_index, exc))
