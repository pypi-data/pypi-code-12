from django.conf.urls import url, include

from rest_framework import routers

from xdjango.contrib.auth import views


router = routers.DefaultRouter()
router.register(r'users', views.UserEmailViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^sessions/$', views.SessionAPIView.as_view()),
]