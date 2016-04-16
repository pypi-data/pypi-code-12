import projex.text
import random

from projex.lazymodule import lazy_import
from ..column import Column

orb = lazy_import('orb')

class AbstractNumericColumn(Column):
    def __init__(self, minimum=None, maximum=None, **kwds):
        super(AbstractNumericColumn, self).__init__(**kwds)

        # used to determine ranging options
        self.__minimum = minimum
        self.__maximum = maximum

    def copy(self):
        out = super(AbstractNumericColumn, self).copy()
        out.setMinimum(self.__minimum)
        out.setMaximum(self.__maximum)
        return out

    def maximum(self):
        return self.__maximum

    def minimum(self):
        return self.__minimum

    def random(self):
        """
        Returns a random value that fits this column's parameters.

        :return: <variant>
        """
        minimum = self.minimum() or 0
        maximum = self.maximum() or 100
        return random.randint(minimum, maximum)

    def setMaximum(self, maximum):
        self.__maximum = maximum

    def setMinimum(self, minimum):
        self.__minimum = minimum

    def validate(self, value):
        if (value is not None and
            (self.__minimum is not None and value < self.__minimum or
             self.__maximum is not None and value > self.__maximum)):
            raise orb.errors.ValueOutOfRange(self.name(), value, self.__minimum, self.__maximum)
        else:
            return super(AbstractNumericColumn, self).validate(value)

    def valueFromString(self, value, extra=None, db=None):
        """
        Converts the inputted string text to a value that matches the type from
        this column type.

        :param      value | <str>
                    extra | <variant>
        """
        try:
            return projex.text.safe_eval(value)
        except ValueError:
            return 0


class DecimalColumn(AbstractNumericColumn):
    TypeMap = {
        'Postgres': 'DECIMAL',
        'SQLite': 'REAL'
    }


class FloatColumn(AbstractNumericColumn):
    TypeMap = {
        'Postgres': 'DOUBLE PRECISION',
        'SQLite': 'REAL'
    }


class IntegerColumn(AbstractNumericColumn):
    TypeMap = {
        'Postgres': 'INTEGER',
        'SQLite': 'INTEGER'
    }

    def __init__(self, minimum=None, maximum=None, **kwds):
        if minimum is None:
            minimum = -(2**31)
        if maximum is None:
            maximum = (2**31) - 1

        super(IntegerColumn, self).__init__(minimum=minimum,
                                            maximum=maximum,
                                            **kwds)


class LongColumn(AbstractNumericColumn):
    TypeMap = {
        'Postgres': 'BIGINT',
        'SQLite': 'INTEGER'
    }

    def __init__(self, minimum=None, maximum=None, **kwds):
        if minimum is None:
            minimum = -(2**63)
        if maximum is None:
            maximum = (2**63) - 1

        super(LongColumn, self).__init__(minimum=minimum,
                                         maximum=maximum,
                                         **kwds)


class EnumColumn(LongColumn):
    def __init__(self, enum=None, **kwds):
        super(EnumColumn, self).__init__(**kwds)

        # define custom properties
        self.__enum = enum

    def copy(self):
        out = super(EnumColumn, self).copy()
        out.setEnum(self.__enum)
        return out

    def enum(self):
        """
        Returns the enumeration that is associated with this column.  This can
        help for automated validation when dealing with enumeration types.

        :return     <projex.enum.enum> || None
        """
        return self.__enum

    def setEnum(self, cls):
        """
        Sets the enumeration that is associated with this column to the inputted
        type.  This is an optional parameter but can be useful when dealing
        with validation and some of the automated features of the ORB system.

        :param      cls | <projex.enum.enum> || None
        """
        self.__enum = cls


Column.registerAddon('Enum', EnumColumn)
Column.registerAddon('Decimal', DecimalColumn)
Column.registerAddon('Float', FloatColumn)
Column.registerAddon('Integer', IntegerColumn)
Column.registerAddon('Long', LongColumn)