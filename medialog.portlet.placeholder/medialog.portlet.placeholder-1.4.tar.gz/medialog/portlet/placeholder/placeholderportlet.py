from plone.app.portlets.browser import formhelper
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope import schema
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from medialog.portlet.placeholder import PlaceholderPortletMessageFactory as _


class IPlaceholderPortlet(IPortletDataProvider):

    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    setheight = schema.Int(title=_(u"Height of portlet"),
                             description=_(u"Height in px"),
                             default=0,
                             required=True)



class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPlaceholderPortlet)

    def __init__(self, setheight=None):
        self.setheight = setheight

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Placeholder Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('placeholderportlet.pt')


class AddForm(formhelper.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    schema = IPlaceholderPortlet
    label = _(u"Add Placeholder Portlet")
    description = _(u"This portlet takes up space.")

    def create(self, data):
        return Assignment(**data)

    
class EditForm(formhelper.EditForm):
    schema = IPlaceholderPortlet
    label = _(u"Edit Placeholder Portlet")
    description = _(u"This portlet takes up space.")

