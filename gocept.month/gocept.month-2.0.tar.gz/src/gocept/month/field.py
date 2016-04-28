from gocept.month import Month
from gocept.month.interfaces import IMonthField
import zope.schema
import zope.interface


@zope.interface.implementer(IMonthField, zope.schema.interfaces.IFromUnicode)
class MonthField(zope.schema.Orderable, zope.schema.Field):
    """Field containing a Month.

    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(IMonthField, MonthField())
    True
    """

    _type = Month

    def fromUnicode(self, str):
        return Month.fromString(str)
