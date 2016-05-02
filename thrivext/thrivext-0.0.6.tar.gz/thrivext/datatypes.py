import arrow


class DateMeta(type):
    """
    Metaclass for the Date class. Defines allowled formats for the instancecheck
    method of the Date class
    """

    DATE_FORMATS = [
        "MM/DD/YYYY",
        "MM/DD/YY",
        "MM-DD-YYYY",
        "MM-DD-YY",
        "MM/D/YYYY",
        "MM/D/YY",
        "MM-D-YYYY",
        "MM-D-YY",
        "YYYY/MM/DD",
        "YYYY/MM/D",
        "YYYY-MM-DD",
        "YYYY-MM-D"
    ]

    def __instancecheck__(self, date_str):
        """
        Checks if 'date_str' is one of the allowed formats.

        :type date_str: str
        :param date_str: String to be checked for date-ness

        :rtype: bool
        :return: True if 'date_str' is one of allowed types
        """

        try:
            if arrow.get(date_str, DateMeta.DATE_FORMATS):
                return True
        except Exception:
            return False


class Date(str):
    """
    Date class that will be passed to the instancecheck method
    """

    __metaclass__ = DateMeta


class TimestampMeta(type):
    """
    Metaclass for Timestamp class. Defines a Timestamp class and way to perform
    instance-checks for this class.
    """
    TS_FORMATS = [
        # "YYYY-MM-DD HH:mm:ssZ",
        # "YYYY-MM-DDTHH:mm:ssZ",
        "YYYY-MM-DD HH:mm:ss",
        "YYYY-MM-DDTHH:mm:ss"
    ]

    def __instancecheck__(self, timestamp_str):
        """
        Checks if 'timestamp_str' is of allowed formats. Currently only ISO8601-like
        formats are allowed.

        :type timestamp_str: str
        :param timestamp_str: String to be checked for timestamp-ness

        :rtype: bool
        :return: True if timestamp_str respresents Timestamp in one of the
                 allowed formats.
        """
        try:
            if arrow.get(timestamp_str, TimestampMeta.TS_FORMATS):
                return True
        except Exception:
            return False


class Timestamp(str):
    """
    Instance of TimestampMeta metaclass. *This* is the actual type that will be
    passed to the instancecheck method.
    """
    __metaclass__ = TimestampMeta


class IntegerMeta(type):
    """
    Meta class for Integer, defines instance check for Integer.
    """

    def __instancecheck__(self, s):
        """
        Checks if 's' is an integer string.

        :type s: str
        :param s: String to be checked for Integer-ness

        :rtype: bool
        :return: True if 's' is an integer
        """
        try:
            return isinstance(s, str) and isinstance(int(s), int)
        except ValueError:
            return False


class Integer(str):
    """
    Instance of the IntegerMeta class. This is the actual class that will
    passed to the instancecheck method.
    """
    __metaclass__ = IntegerMeta


class FloatMeta(type):
    """
    Metaclass for float, defines instance check for float
    """

    def __instancecheck__(self, s):
        """
        Checks if 's' is a Float

        :type s: str
        :param s: String to be checked for float-ness

        :rtype: bool
        :return: True if string s is a float
        """

        try:
            return isinstance(s, str) and isinstance(float(s), float)
        except ValueError:
            return False


class Float(str):
    """
    Instance of the FloatMeta class. This is the actual class that will
    passed to the instancecheck method.
    """
    __metaclass__ = FloatMeta


class BooleanMeta(type):
    """
    Metaclass for Boolean types, defines instance check for Boolean values
    """

    TRUTHVALUES = ["TRUE", "true", "t", "T", "1", "y", "yes", "YES",
                   "FALSE", "false", "f", "F", "0", "n", "no", "NO"]

    def __instancecheck__(self, s):
        """
        Checks if 's' is a boolean. Boolean is defined as belonging to
        specific set of strings

        :type s: str
        :param s: String to be checked for bool-ness

        :rtype: bool
        :return: True if string s is a valid boolean
        """
        try:
            return s in BooleanMeta.TRUTHVALUES
        except ValueError:
            return False


class Boolean(str):
    """
    Boolean class that will be passed to the instancecheck method.
    """

    __metaclass__ = BooleanMeta