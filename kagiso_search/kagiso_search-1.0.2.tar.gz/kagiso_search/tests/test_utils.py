from django.test import TestCase
from wagtail.wagtailcore.models import Page

from ..utils import pg_full_text_search


class PGFullTextSearchTestCase(TestCase):

    def test_search_no_results_found(self):
        home_page = Page.objects.get(slug='home')
        result = pg_full_text_search('Justin Bieber', home_page)

        assert list(result) == []

    def test_search_removes_ampersands(self):
        home_page = Page.objects.get(slug='home')
        result = pg_full_text_search('Justin & Bieber', home_page)

        assert list(result) == []

    def test_search_results_found(self):
        home_page = Page.objects.get(slug='home')
        bieber_article = Page(
            title='Justin Bieber',
            slug='justin-bieber'
        )
        home_page.add_child(instance=bieber_article)

        result = pg_full_text_search('Justin Bieber', home_page)

        assert list(result) == [bieber_article]

    def test_search_scopes_to_site_root_page(self):
        home_page = Page.objects.get(slug='home')
        root_article = Page(
            title='Justin Bieber',
            slug='justin-bieber'
        )
        non_root_article = Page(
            depth=0,
            path='0002',
            title='Justin Bieber Again',
            slug='justin-bieber-again'
        )
        home_page.add_child(instance=root_article)
        non_root_article.save()

        result = pg_full_text_search('Justin Bieber', home_page)

        assert list(result) == [root_article]
