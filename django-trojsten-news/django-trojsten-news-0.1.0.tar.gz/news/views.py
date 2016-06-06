from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.views.generic import ListView

from news.models import Entry
from news.constants import NEWS_PAGINATE_BY


class EntryListView(ListView):
    model = Entry
    template_name = 'news/index.html'
    context_object_name = 'news_entries'
    paginate_by = NEWS_PAGINATE_BY

    def get_queryset(self):
        try:
            return self.model.objects.filter(
                sites__id__exact=get_current_site(self.request).id
            )
        except Site.DoesNotExist:
            return self.model.objects.all()
