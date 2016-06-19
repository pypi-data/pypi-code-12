from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from hosted_plugins import views

router = routers.DefaultRouter if settings.DEBUG == True else routers.SimpleRouter

plugins_router = router(trailing_slash=False)
plugins_router.register(r'updates', views.UpdateViewSet, base_name='update')

urlpatterns = [
    url(r'^(?P<platform>[\w-]+)/', include(plugins_router.urls, namespace='hosted-plugins')),
]
