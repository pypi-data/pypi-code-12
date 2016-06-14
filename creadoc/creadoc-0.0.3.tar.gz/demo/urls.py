# coding: utf-8
import os
from django.conf import settings
from django.conf.urls import patterns
from m3.actions import urls


handler500 = 'm3.helpers.logger.catch_error_500'


urlpatterns = patterns(
    '',
    (
        r'^downloads/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}
    ),
    (
        r'^m3static/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': os.path.join(settings.M3_ROOT, 'static')}
    ),
    (r'^$', 'demo.app.views.workspace'),
)
urlpatterns += urls.get_app_urlpatterns()
