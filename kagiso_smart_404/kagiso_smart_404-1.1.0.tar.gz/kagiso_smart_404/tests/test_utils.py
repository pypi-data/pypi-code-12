from datetime import datetime

from django.test import TestCase
from wagtail.wagtailcore.models import Page

from ..utils import (
    page_slug,
    slug_matches_one_page_exactly,
    suggest_page_from_misspelled_slug
)


def test_page_slug_gets_page_specific_slug_from_full_path():
    assert page_slug('/news/') == 'news'
    assert page_slug('/news') == 'news'
    assert page_slug('news') == 'news'

    assert page_slug('/news/my-article/') == 'my-article'
    assert page_slug('/news/my-article') == 'my-article'
    assert page_slug('news/my-article') == 'my-article'

    assert page_slug('/favicon.ico') == 'favicon.ico'


class SlugMatchesOnePageExactlyTest(TestCase):

    def test_matching_slug_returns_single_page(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=article)

        result = slug_matches_one_page_exactly(
            '/shows/workzone-with-bridget-masinga/', home_page)

        assert result == article

    def test_multiple_slug_depth(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=article)

        result = slug_matches_one_page_exactly(
            '/test/post/page/shows/workzone-with-bridget-masinga/', home_page)

        assert result == article

    def test_multiple_articles_with_same_slug_returns_none(self):
        home_page = Page.objects.get(slug='home')
        article_index_one = Page(
            title='First Index',
            slug='first-index'
        )
        article_index_two = Page(
            title='Second Index',
            slug='second-index'
        )
        home_page.add_child(instance=article_index_one)
        home_page.add_child(instance=article_index_two)

        article_one = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        article_two = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )

        article_index_one.add_child(instance=article_one)
        article_index_two.add_child(instance=article_two)

        result = slug_matches_one_page_exactly(
            '/shows/workzone-with-bridget-masinga/', home_page)

        assert result is None

    def test_no_matching_slug(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        home_page.add_child(instance=article)

        result = slug_matches_one_page_exactly(
            '/post/no-result/', home_page)

        assert result is None

    def test_slug_scopes_to_site(self):
        home_page = Page.objects.get(slug='home')
        article_index_one = Page(
            title='First Index',
            slug='first-index'
        )
        article_index_two = Page(
            title='Second Index',
            slug='second-index'
        )
        home_page.add_child(instance=article_index_one)
        home_page.add_child(instance=article_index_two)

        article_one = Page(
            title='Article One',
            slug='article-one'
        )
        article_two = Page(
            title='Article Two',
            slug='article-two'
        )

        article_index_one.add_child(instance=article_one)
        article_index_two.add_child(instance=article_two)

        result = slug_matches_one_page_exactly(
            '/shows/article-one/', article_index_two)

        assert result is None


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
