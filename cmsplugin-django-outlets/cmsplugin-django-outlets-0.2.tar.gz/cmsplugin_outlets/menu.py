"""Custom menu for cmsplugin_outletes"""
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from outlets.models import OutletCountry


class OutletsMenu(CMSAttachMenu):

    name = _("outlets menu")

    def get_nodes(self, request):
        nodes = []
        for counter, country in enumerate(OutletCountry.objects.all()):
            node = NavigationNode(country.name, reverse('outlets_list',
                                  kwargs={'slug': country.slug}), counter)
            nodes.append(node)
        return nodes


menu_pool.register_menu(OutletsMenu)
