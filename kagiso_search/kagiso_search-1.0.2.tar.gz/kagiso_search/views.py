from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import render
from django.views.decorators.cache import never_cache


from .utils import pg_full_text_search


@never_cache
def search(request):
    search_query = request.GET.get('query')
    page_number = request.GET.get('page', 1)
    search_results = []

    if search_query:
        search_results = pg_full_text_search(
            search_query,
            request.site.root_page
        )
        # RawQuerySet has no len() needed by the paginator
        search_results = list(search_results)

    paginator = Paginator(search_results, settings.ITEMS_PER_PAGE)
    try:
        page = paginator.page(page_number)
        # Only call `.specific` on page items rather than whole dataset
        # as specific is extremely slow
        items = []
        for item in page.object_list:
            specific_item = item.specific
            specific_item.headline = item.headline
            items.append(specific_item)
        page.object_list = items
    except EmptyPage:
        # Show empty search page, like Tumblr and co.
        pass

    return render(request, 'kagiso_search/search_results.html', {
        'search_query': search_query,
        'search_results': page,
    })
