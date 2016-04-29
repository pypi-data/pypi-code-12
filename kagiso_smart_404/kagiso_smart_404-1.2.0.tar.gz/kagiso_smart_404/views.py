from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render

from .utils import (
    suggest_page_from_misspelled_slug
)


def not_found(request):  # pragma: no cover
    slug = request.path
    root_page = request.site.root_page.specific

    suggested_pages = suggest_page_from_misspelled_slug(slug, root_page)

    if len(suggested_pages) == 1:
        intended_url = suggested_pages[0].url
        return HttpResponsePermanentRedirect(redirect_to=intended_url)

    data = {'suggested_pages': suggested_pages}
    return render(request, '404.html', data, status=404)
