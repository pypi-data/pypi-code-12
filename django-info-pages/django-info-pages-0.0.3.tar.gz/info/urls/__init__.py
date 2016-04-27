from django.conf.urls import include, url

urlpatterns = [
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url('^blog/', include('info.urls.blog')),
    url('^info/', include('info.urls.pages')),
]
