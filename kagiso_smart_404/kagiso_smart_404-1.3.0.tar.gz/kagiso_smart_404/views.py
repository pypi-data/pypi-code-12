from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render

from .utils import (
    slug_matches_one_page_exactly,
    suggest_page_from_misspelled_slug
)


def not_found(request):  # pragma: no cover
    slug = request.path
    root_page = request.site.root_page.specific

    suggested_pages = suggest_page_from_misspelled_slug(slug, root_page)

    # Has a content person moved a page around the tree with the page slug
    # remaining as per before, if so redirect to page with matching slug
    exact_match = slug_matches_one_page_exactly(slug, root_page)
    if exact_match:
        return HttpResponsePermanentRedirect(redirect_to=exact_match.url)

    data = {'suggested_pages': suggested_pages}
    return render(request, '404.html', data, status=404)
