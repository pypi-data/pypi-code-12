from django.conf.urls import url

from kagiso_search import views

urlpatterns = [
    '',
    url(r'^search/', views.search, name='search'),
]
