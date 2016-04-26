__author__ = 'vinay'
from django.conf import settings
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^cms/ajax/save/(?P<save_type>.+)/$',
        views.save, name='save_cms_content'),
    url(r'^.+{}'.format(r'/$' if settings.APPEND_SLASH else r''),
        views.cms_page_index, name='cms_index'),
]
