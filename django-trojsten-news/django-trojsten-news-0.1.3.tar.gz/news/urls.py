from django.conf.urls import url

from news.feeds import NewsFeed
from news.views import EntryListView

urlpatterns = [
    url(r'^strana/(?P<page>[0-9]+)/$', EntryListView.as_view(),
        name='news_list'),
    url(r'^feed/$', NewsFeed(), name='news_feed'),
]
