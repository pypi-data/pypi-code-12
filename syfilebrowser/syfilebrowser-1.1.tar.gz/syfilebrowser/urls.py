from __future__ import unicode_literals

from django.conf.urls import *

urlpatterns = patterns('',

    # syfilebrowser urls
    url(r'^browse/$', 'syfilebrowser.views.browse', name="fb_browse"),
    url(r'^mkdir/', 'syfilebrowser.views.mkdir', name="fb_mkdir"),
    url(r'^upload/', 'syfilebrowser.views.upload', name="fb_upload"),
    url(r'^rename/$', 'syfilebrowser.views.rename', name="fb_rename"),
    url(r'^delete/$', 'syfilebrowser.views.delete', name="fb_delete"),
    url(r'^check_file/$', 'syfilebrowser.views._check_file', name="fb_check"),
    url(r'^upload_file/$', 'syfilebrowser.views._upload_file', name="fb_do_upload"),

)
