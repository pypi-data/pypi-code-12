from __future__ import unicode_literals

from django.conf.urls import *

urlpatterns = patterns('',

    # wlfilebrowser urls
    url(r'^browse/$', 'wlfilebrowser.views.browse', name="fb_browse"),
    url(r'^mkdir/', 'wlfilebrowser.views.mkdir', name="fb_mkdir"),
    url(r'^upload/', 'wlfilebrowser.views.upload', name="fb_upload"),
    url(r'^rename/$', 'wlfilebrowser.views.rename', name="fb_rename"),
    url(r'^delete/$', 'wlfilebrowser.views.delete', name="fb_delete"),
    url(r'^check_file/$', 'wlfilebrowser.views._check_file', name="fb_check"),
    url(r'^upload_file/$', 'wlfilebrowser.views._upload_file', name="fb_do_upload"),

)
