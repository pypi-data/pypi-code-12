from datetime import datetime

from django.test import TestCase
from wagtail.wagtailcore.models import Page

from ..utils import (
    suggest_page_from_misspelled_slug
)


class SuggestPageFromMisspelledSlugTest(TestCase):

    def test_no_similar_slugs_returns_empty_array(self):
        home_page = Page.objects.get(slug='home')
        result = suggest_page_from_misspelled_slug(
            '/no-such-page/', home_page)

        assert result == []

    def test_matching_slug_returns_page(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=article)

        result = suggest_page_from_misspelled_slug(
            '/workzon-bridget-masing/', home_page)

        assert article in result

    def test_multiple_matches_returns_best_matching_page(self):
        home_page = Page.objects.get(slug='home')
        better_matching_article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        poorer_matching_article = Page(
            title='Bridget Masinga',
            slug='bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=better_matching_article)
        home_page.add_child(instance=poorer_matching_article)

        result = suggest_page_from_misspelled_slug(
            '/workzon-bridget-masing/', home_page)

        assert better_matching_article in result

    def test_multiple_matches_returns_max_3_top_matches(self):
        home_page = Page.objects.get(slug='home')
        ok_match_1 = Page(
            title='Bridget Masinga',
            slug='bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        ok_match_2 = Page(
            title='Bridget Masinga Again',
            slug='bridget-masinga-again',
            live=True,
            first_published_at=datetime.now()
        )
        ok_match_3 = Page(
            title='More Bridget Masinga',
            slug='more-bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        # If slicing is commented out this result is returned for a slug '/bridget'! # noqa
        poorer_match = Page(
            title='Bridge Building',
            slug='bridge-building',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=ok_match_1)
        home_page.add_child(instance=ok_match_2)
        home_page.add_child(instance=ok_match_3)
        home_page.add_child(instance=poorer_match)

        result = suggest_page_from_misspelled_slug(
            '/bridget', home_page)

        assert len(result) == 3
        assert poorer_match not in result
