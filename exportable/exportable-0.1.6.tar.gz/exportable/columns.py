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
import itertools
import datetime
import dateutil.parser

CREATION_COUNTER = itertools.count()


class Column(object):
    def __init__(self, ctype, label=None, cellfunc=None, rowfunc=None, verbose_name=None, _creation_counter=None):
        """
        @param ctype: type yielded by rowfunc/cellfunc.
        @param label: alphanumeric label for column (often used to access datastructures)
        @param cellfunc: if defined, modify value returned by rowfunc()
        @param rowfunc: used to access the correct property in a row (mostly set by Table)
        @param verbose_name: often used in renderers for column names
        """
        self.type = ctype
        self.label = label
        self.cellfunc = cellfunc
        self.rowfunc = rowfunc
        self.verbose_name = label if verbose_name is None else verbose_name

        # Index refers to the index of the column including None-columns
        self._index = 0

        # View index refers to the index of the column excluding None-columns
        self._view_index = 0

        # Creation counter is kept to determine the order in declared tables
        self._creation_counter = next(CREATION_COUNTER) if _creation_counter is None else _creation_counter

    def from_str(self, s):
        """Convert value from str. Might be used by importers which support all formats."""
        return self.type(s) if s else None

    def to_str(self, value):
        """Convert value into string representation. Might be used by exporters which file
        format does not support types or specific types."""
        return "" if value is None else str(value)

    def __copy__(self):
        # Copy be instantiating a new class
        copied = self.__class__(
            label=self.label, cellfunc=self.cellfunc,
            rowfunc=self.rowfunc, verbose_name=self.verbose_name,
            _creation_counter=self._creation_counter
        )

        # Copy all remaining attributes as well
        for attr_name, value in self.__dict__.items():
            if attr_name not in copied.__dict__:
                copied.__dict__[attr_name] = value

        return copied


    def __repr__(self):
        return "<{}(label={})>".format(self.__class__.__name__, self.label)


class TextColumn(Column):
    def __init__(self, label=None, **kwargs):
        super().__init__(str, label, **kwargs)

    def to_str(self, value):
        return value


class IntColumn(Column):
    def __init__(self, label=None, **kwargs):
        super().__init__(int, label, **kwargs)


class FloatColumn(Column):
    def __init__(self, label=None, **kwargs):
        super().__init__(float, label, **kwargs)


class DateColumn(Column):
    def __init__(self, label=None, **kwargs):
        super().__init__(datetime.date, label, **kwargs)

    def from_str(self, s) -> datetime.date:
        return dateutil.parser.parse(s).date() if s else None

    def to_str(self, date: datetime.date):
        return date.isoformat()


class DateTimeColumn(Column):
    def __init__(self, label=None, **kwargs):
        super().__init__(datetime.datetime, label, **kwargs)

    def from_str(self, s) -> datetime.datetime:
        return dateutil.parser.parse(s) if s else None

    def to_str(self, time: datetime.datetime):
        return time.isoformat()
