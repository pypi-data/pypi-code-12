# coding=utf-8
from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^cms/ajax/save/draft/$', views.save,
        name='save_cms_content', kwargs={'save_type': 'draft'}),
    url(r'^cms/ajax/save/publish/$', views.save,
        name='publish_cms_content', kwargs={'save_type': 'publish'}),
    url(r'^.+{}|^$'.format(r'/$' if settings.APPEND_SLASH else r''),
        views.cms_page_index, name='cms_index'),
]
