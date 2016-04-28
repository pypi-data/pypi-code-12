# coding: utf-8
from gocept.month import Month
from zope.formlib.textwidgets import escape, TextWidget
from zope.formlib.widget import DisplayWidget, renderElement
from zope.formlib.interfaces import (
    IDisplayWidget, IInputWidget, ConversionError)
import gocept.month.field
import z3c.form.browser.text
import z3c.form.error
import z3c.form.interfaces
import z3c.form.widget
import zope.component
import zope.i18nmessageid
import zope.interface
import zope.schema.interfaces

_ = zope.i18nmessageid.MessageFactory("gocept")


class MonthConversionError(ConversionError):
    __doc__ = _(u"Format muss MM/JJJJ sein (z.B. 11/2005 für November 2005).")

    def doc(self):
        return self.__class__.__doc__


@zope.interface.implementer(IDisplayWidget)
class MonthDisplayWidget(DisplayWidget):
    """Widget displaying the contents of an IMonthField."""

    cssClass = "month"

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if content == self.context.missing_value:
            return ""
        content = str(content)
        return renderElement("span",
                             contents=escape(content),
                             cssClass=self.cssClass)


@zope.interface.implementer(IInputWidget)
class MonthEditWidget(TextWidget):
    """Widget displaying the contents of an IMonthField. """

    def _toFieldValue(self, input):
        try:
            return Month.fromString(input)
        except ValueError as error:
            raise MonthConversionError(error)


class MonthWidget(z3c.form.browser.text.TextWidget):
    """Widget displaying the contents of an IMonthField for z3c.form. """


@zope.component.adapter(zope.schema.interfaces.IField,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def MonthFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, MonthWidget(request))


class MonthErrorViewSnippet(z3c.form.error.ErrorViewSnippet):

    zope.component.adapts(
        ValueError, None, None, gocept.month.field.MonthField, None,
        None)

    def createMessage(self):
        return MonthConversionError.__doc__
