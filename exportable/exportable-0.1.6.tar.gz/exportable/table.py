###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################
import copy
import datetime
import functools
import itertools
from operator import itemgetter, attrgetter

from typing import Iterable, Any, Sequence, Optional, Container
from exportable.columns import Column


def get_exporter(exporter):
    if isinstance(exporter, str):
        from exportable.exporters import get_exporter_by_extension
        return get_exporter_by_extension(exporter)
    return exporter


class Table:
    """
    Abstract class. Subclasses only need to implement get_value().

    @param rows: data source. Format depends on the subclass.
    @param lazy: if True, no random access is allowed. This is the preferred way of initializing
                 a table, as it won't hold the whole table in memory.
    @param size_hint: length of rows. Is used by exporters to determine progress, and some other
                      exporters to write proper binary files.
    """
    def __init__(self, rows: Iterable[Any], columns: Sequence[Column]=(), lazy=True, size_hint=None):
        # If no size_hint is given, try to guess the size by querying rows.
        if size_hint is None:
            try:
                self.size_hint = len(rows)
            except TypeError:
                self.size_hint = None
        else:
            self.size_hint = size_hint

        self.lazy = lazy
        self._rows = iter(rows) if lazy else list(rows)
        self._column_counter = itertools.count()
        self._columns = []

        for column in columns:
            self.add_column(column)

    def __len__(self):
        if self.size_hint is None:
            raise TypeError("No size_hint has been given to this table, and no size could be determined from (lazy?) source.")
        return self.size_hint

    def to_strict(self):
        """Convert this (lazy) exportable into a non-lazy (strict) one."""
        if self.lazy:
            self._rows = list(self._rows)
            self.lazy = False

    @property
    def columns(self) -> Iterable[Column]:
        return filter(None, self._columns)

    @property
    def rows(self):
        return ([self.get_value(row, column) for column in self.columns] for row in self._rows)

    def get_value(self, row, column: Column):
        cfunc = column.cellfunc
        value = column.rowfunc(row)
        return cfunc(value) if cfunc else value

    def add_column(self, column: Column):
        column = copy.copy(column)
        column._index = next(self._column_counter)
        column._view_index = self._columns[-1]._view_index + 1 if self._columns else 0
        self._columns.append(column)
        return column

    def dump(self, fo, exporter, filename_hint=None, encoding_hint="utf-8"):
        return get_exporter(exporter)().dump(self, fo, filename_hint=filename_hint, encoding_hint=encoding_hint)

    def dumps(self, exporter, filename_hint=None, encoding_hint="utf-8"):
        return get_exporter(exporter)().dumps(self, filename_hint=filename_hint, encoding_hint=encoding_hint)


class ListTable(Table):
    """
    >>> from exportable.columns import IntColumn
    >>>
    >>> table = ListTable(
    >>>     rows=[
    >>>         [1, 2, 3],
    >>>         [4, 5, 6]
    >>>     ],
    >>>     columns=[
    >>>         IntColumn(),
    >>>         None,
    >>>         IntColumn()
    >>>      ]
    >>> )
    >>>
    >>> list(table.rows)
    >>> [[1, 3], [4, 6]]

    @param rows: list of lists
    @param columns: if a column is None, skip a field in each row
    """
    def add_column(self, column: Optional[Column]):
        if column is not None:
            column = super().add_column(column)
            if column.rowfunc is None:
                column.rowfunc = itemgetter(column._index)
        else:
            next(self._column_counter)


class DictTable(Table):
    """
    Similar to ListTable, but uses a list of dicts.

    @param rows: list of dicts
    @param columns: list of columns. The label of a column is used to access dictionary.
    """
    def add_column(self, column: Column):
        column = super().add_column(column)
        if column.rowfunc is None:
            column.rowfunc = itemgetter(column.label)


class AttributeTable(Table):
    """
    Similar to ListTable, but uses a list of objects.

    @param rows: list of rows
    @param columns: list of columns. The label of a column is used to access attributes.
    """
    def add_column(self, column: Column):
        column = super().add_column(column)
        if column.rowfunc is None:
            column.rowfunc = attrgetter(column.label)


class WrappedTable:
    """
    Wrapped tables wrap, like the name implies, table objects. Although they do not inherit from
    Table, the support the same methods through attribute proxying. Wrapped tables offer
    additional functionality to tables, while not concerning themselves with the underlying data
    structure.
    """
    def __init__(self, table):
        self.table = table

        # Copy hot function to prevent loads of redirects
        self.get_value = table.get_value

    def __getattr__(self, name):
        return getattr(self.table, name)


class SortedTable(WrappedTable):
    """A sorted table sorts its rows according to a user defined function."""
    def __init__(self, table: Table, key, reverse=False):
        """
        @param table: table to wrap
        @param key: lambda function passed to sorted(). Is given a row.
        @param reverse: reverse sorting.
        """
        super(SortedTable, self).__init__(table)
        self.key = key
        self.reverse = reverse
        self.table.to_strict()

    @property
    @functools.lru_cache()
    def rows(self):
        return sorted(self.table.rows, key=self.key, reverse=self.reverse)


def _get_declared_columns(cls):
    for attr_name in dir(cls):
        if not attr_name.startswith("_"):
            column = getattr(cls, attr_name)
            if isinstance(column, Column):
                if column.label is None:
                    column.label = attr_name
                yield column


@functools.lru_cache()
def get_declared_columns(cls):
    return tuple(sorted(_get_declared_columns(cls), key=lambda c: c._creation_counter))


def filter_columns(columns: Iterable[Column],
                   include: Optional[Container[str]]=None,
                   exclude: Optional[Container[str]]=None):
    """
    Include or exclude columns based on their labels.
    """
    if include and exclude:
        raise ValueError("Pass either include or exclude, not both.")
    elif include is None and exclude is None:
        return columns
    elif not include and not exclude:
        raise ValueError("Pass either include or exclude, not neither.")
    elif include:
        return (c for c in columns if c.label in include)
    elif exclude:
        return (c for c in columns if c.label not in exclude)
    else:
        raise RuntimeError("Not reachable?")


class DeclaredTable(WrappedTable):
    """A declared table defines columns on declaration time. For example:

    >>> from exportable import columns
    >>>
    >>> class ExampleTable(DeclaredTable):
    >>>    title = columns.TextColumn()
    >>>    time = columns.DateTimeColumn()
    >>>
    >>> table = ExampleTable(ListTable, rows=[
    >>>     ["Foo", datetime.datetime.now()],
    >>>     ["Bar", datetime.datetime.now()],
    >>> ])

    Declared tables are not dependent on one specific data structure, as it is a WrappedTable.
    """
    def __init__(self, table_cls, rows, include=None, exclude=None, lazy=True, size_hint=None):
        """

        @param table_cls: class to use to get data from rows (ex: ListTable, DictTable, etc)
        @param include: column labels to include
        @param exclude: column labels to exclude
        """
        columns = filter_columns(self._get_columns(), include=include, exclude=exclude)
        super().__init__(table_cls(rows, columns, lazy=lazy, size_hint=size_hint))

    @classmethod
    def _get_columns(cls):
        return get_declared_columns(cls)
