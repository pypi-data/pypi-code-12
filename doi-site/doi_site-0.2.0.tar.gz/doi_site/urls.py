""" The URL mappings. """

from django.conf.urls import include, url
from django.contrib import admin

from datasets.views import Mint
from doi_site.views import DoiList, Domains, HomeView, Notes
from mds.views import DoiView, DoiDetail, MetadataPost, MetadataView, MediaView


# pylint: disable=invalid-name
urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^index$', HomeView.as_view(), name='index'),

    url(r'^admin/', include(admin.site.urls)),

    # web
    url(r'^doilist$', DoiList.as_view(), name='doi_list'),
    url(r'^domains$', Domains.as_view(), name='domains'),
    url(r'^mint$', Mint.as_view(), name='mint'),
    url(r'^notes$', Notes.as_view(), name='notes'),

    # MDS
    url(r'^doi$', DoiView.as_view(), name='doi_view'),
    url(r'^doi/', DoiDetail.as_view(), name='doi_detail'),
    url(r'^metadata$', MetadataPost.as_view(), name='metadata_post'),
    url(r'^metadata/', MetadataView.as_view(), name='metadata_view'),
    url(r'^media/', MediaView.as_view(), name='media_view'),

    url(r'^accounts/login/$', 'doi_site.views.login', name='login'),
    url(r'^logout/$', 'doi_site.views.logout', name='logout'),

    url(r'', HomeView.as_view()),
]
