# -*- coding: utf-8 -*-
"""Terms & Conditions Widget Implementation"""

# zope imports
from Products.Five.browser import BrowserView
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from plone import api
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.interfaces import (
    IFieldWidget,
    IFormLayer,
)
from z3c.form.widget import FieldWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import (
    implementer,
    implementer_only,
)
from zope.schema.interfaces import IBool
from zope.component import adapter

# local imports
from plone.mls.listing.browser.tcwidget.interfaces import ITCWidget


class RenderTCWidget(ViewMixinForTemplates, BrowserView):
    index = ViewPageTemplateFile('tcwidgetwrapper.pt')


@implementer_only(ITCWidget)
class TCWidget(SingleCheckBoxWidget):
    """Single Input type checkbox widget implementation."""

    klass = u'terms-conditions-widget'
    target = None

    def tc_link(self):
        if not self.target:
            return

        portal = api.portal.get()
        path = str(self.target)
        if path.startswith('/'):
            path = path[1:]
        item = portal.restrictedTraverse(path, default=False)
        if not item:
            return
        return {
            'label': item.title,
            'url': item.absolute_url(),
        }


@adapter(IBool, IFormLayer)
@implementer(IFieldWidget)
def TCFieldWidget(field, request):
    """IFieldWidget factory for TCWidget."""
    widget = FieldWidget(field, TCWidget(request))
    # widget.label = u''  # don't show the label twice
    return widget
