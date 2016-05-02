from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

admin.autodiscover()

from example.views import BlogViewSet, EntryViewSet, AuthorViewSet, CommentViewSet

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'blogs', BlogViewSet)
router.register(r'entries', EntryViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
]
