"""CMS apphook for the django-outlets app."""
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from . import menu


class OutletsApphook(CMSApp):
    name = _("Outlets Apphook")
    urls = ["outlets.urls"]
    menus = [menu.OutletsMenu]


apphook_pool.register(OutletsApphook)
