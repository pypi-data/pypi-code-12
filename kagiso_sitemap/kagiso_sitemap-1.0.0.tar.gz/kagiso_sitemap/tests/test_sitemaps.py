from django.test import TestCase
from wagtail.wagtailcore.models import Page

from ..sitemaps import KagisoSitemap


class KagisoSitemapTestCase(TestCase):

    def test_items_returns_all_pages_except_root(self):
        root_page = Page.objects.get(slug='root')
        home_page = Page.objects.get(slug='home')
        site_map = KagisoSitemap()

        result = site_map.items()

        assert root_page  # Check that it exists...
        assert list(result) == [home_page]

    def test_lastmod_returns_first_published_at(self):
        home_page = Page.objects.get(slug='home')
        site_map = KagisoSitemap()

        result = site_map.lastmod(home_page)

        assert result == home_page.first_published_at

    def test_location_returns_page_url(self):
        home_page = Page.objects.get(slug='home')
        site_map = KagisoSitemap()

        result = site_map.location(home_page)

        assert result == ' ' + home_page.url
