from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^netjsonconfig/schema\.json$', views.schema, name='schema'),
]
