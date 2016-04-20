# -*- coding: utf-8 -*-
from zope.interface import Interface, implements, implementer
from zope.component import adapter
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget


class ITaxonomySelect2Widget(Interface):
    """ Marker interface for the taxonomy select widget """


class TaxonomySelect2Widget(SelectWidget):
    implements(ITaxonomySelect2Widget, interfaces.ISelectWidget)

    noValueToken = ''
    size = 5


@adapter(zope.schema.interfaces.ISequence, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def TaxonomySelect2FieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, TaxonomySelect2Widget(request))
