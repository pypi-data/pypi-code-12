from content.views import PageUpdateView
from django.conf.urls import *

defaultpatterns = patterns('', ('^', include('content.urls')),)

gallerypatterns = patterns('content.views',
    url(r'^(?P<slug>[\w-]+)/(?P<id>\d+)$', 'media_detail', name="media-detail"),
    url(r'^(?P<slug>[\w-]+)/$', 'album_detail', name="album-detail"),
    url(r'^$', 'album_list', name="album-detail"),
)


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+|new)/save/', PageUpdateView.as_view(), name="content-save")
)
