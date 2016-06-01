from django.conf.urls import include, url

urlpatterns = [
    url(r'^zebra/', include('zebra.urls', namespace="zebra", app_name='zebra')),
    url(r'', include('marty.urls', namespace="marty", app_name='marty')),
]
