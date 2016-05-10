from datetime import date
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

class TopperViewlet(ViewletBase):
    index = ViewPageTemplateFile('topperportlets.pt')

    def update(self):
        super(TopperViewlet, self).update()
        self.year = date.today().year

    def render_topper_portlets(self):
        """
        You might ask, why is this necessary. Well, let me tell you a story...

        plone.app.portlets, in order to provide @@manage-portlets on a context,
        overrides the IPortletRenderer for the IManageContextualPortletsView view.
        See plone.portlets and plone.app.portlets

        Seems fine right? Well, most of the time it is. Except, here. Previously,
        we were just using the syntax like `provider:plone.footerportlets` to
        render the footer portlets. Since this tal expression was inside
        a viewlet, the view is no longer IManageContextualPortletsView when
        visiting @@manage-portlets. Instead, it was IViewlet.
        See zope.contentprovider

        In to fix this short coming, we render the portlet column by
        manually doing the multi adapter lookup and then manually
        doing the rendering for the content provider.
        See zope.contentprovider
        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name='plone.topperportlets')
        portlet_manager.update()
        return portlet_manager.render()
        
        
        
class AboveViewlet(ViewletBase):
    index = ViewPageTemplateFile('aboveportlets.pt')

    def update(self):
        super(AboveViewlet, self).update()
        self.year = date.today().year

    def render_above_portlets(self):
        """

        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name='plone.aboveportlets')
        portlet_manager.update()
        return portlet_manager.render()