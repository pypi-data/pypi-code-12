# coding=utf-8

from django.conf.urls import url

from . import settings as _settings
from . import views as _views


urlpatterns = [
    url(
        r'(?P<name>\w+\.(?:{0}))$'.format(r'|'.join(_settings.EXTENSION_CONTENT_TYPE_MAP.keys())),
        _views.leonid_file_view, name='leonid_file'
    ),
]
