from django.conf.urls import include, url
from . import views

app_name = 'Reviewable'
urlpatterns = [
    url(r'(?P<pk>[0-9]+)/$', views.ReviewDetail.as_view(), name='review-detail'),
    url(r'(?P<pk>[0-9]+)/update$', views.ReviewUpdate.as_view(), name='review-update'),
    url(r'(?P<pk>[0-9]+)/delete$', views.ReviewDelete.as_view(), name='review-delete'),
    url(r'(?P<content_type>[\w-]+)/(?P<pk>[0-9]+)/create$', views.ReviewCreate.as_view(), name='review-create'),
    url(r'(?P<content_type>[\w-]+)/(?P<pk>[0-9]+)/list$', views.ReviewList.as_view(), name='review-list'),
]

