from django.conf.urls import patterns, url
from media.models import Photo, PhotoSet
from django.views.generic import DetailView, ListView


class PhotoDetailView(DetailView):
    queryset = Photo.objects.all()


class PhotoListView(ListView):
    queryset = Photo.objects.all()


class PhotoSetDetailView(DetailView):
    queryset = PhotoSet.objects.all(),


class PhotoSetListView(ListView):
    queryset = PhotoSet.objects.all(),


urlpatterns = patterns('',
    url(r'^sets/(?P<slug>[-\w]+)/$',
        view=PhotoSetDetailView.as_view(),
        name='photo_set_detail',
    ),
    url(r'^sets/$',
        view=PhotoSetListView.as_view(),
        name='photo_set_list',
    ),
    url(r'^(?P<slug>[-\w]+)/$',
        view=PhotoDetailView.as_view(),
        name='photo_detail',
    ),
    url(r'^$',
        view=PhotoListView.as_view(),
        name='photo_list',
    ),
)
