from ftw.mobile.buttons import BaseButton
from ftw.servicenavigation import _
from ftw.servicenavigation.viewlet import ServiceNavigation


class ServiceNavigationButton(BaseButton):

    def label(self):
        return _(u"Service Navigation")

    def position(self):
        return 900

    def data(self):
        viewlet = ServiceNavigation(self.context, self.request, None, None)
        links = viewlet.get_service_links()
        return links
