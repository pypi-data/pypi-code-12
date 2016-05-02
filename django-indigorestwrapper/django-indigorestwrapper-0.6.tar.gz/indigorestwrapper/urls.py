from django.conf.urls import url
from indigorestwrapper import views

urlpatterns = [
    url(r'^devices/$', views.device_list),
    url(r'^indigo_devices/$', views.indigo_device_list),
    url(r'^device/(?P<id>[0-9]+)/$', views.device),
    url(r'^device_history/(?P<id>[0-9]+)/$', views.device_history),
]