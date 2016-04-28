from datetime import date
from gocept.month.adapter import Date, BuiltinStr
from gocept.month.interfaces import IDate, IMonth
import zope.component
import zope.interface


def setUpZCA():
    zope.interface.classImplements(date, IDate)
    zope.component.provideAdapter(Date, (IDate,), IMonth)
    zope.component.provideAdapter(BuiltinStr, (str,), IMonth)


def tearDownZCA():
    zope.component.getSiteManager().unregisterAdapter(
        Date, (IDate,), IMonth)
    zope.component.getSiteManager().unregisterAdapter(
        BuiltinStr, (str,), IMonth)
