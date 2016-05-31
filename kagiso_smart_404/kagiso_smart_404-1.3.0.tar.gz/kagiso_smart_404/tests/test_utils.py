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

    assert page_slug('/news/myarticle/') == 'myarticle'
    assert page_slug('/news/myarticle') == 'myarticle'
    assert page_slug('news/myarticle') == 'myarticle'

    assert page_slug('/favicon.ico') == 'favicon.ico'


class SlugMatchesOnePageExactlyTest(TestCase):

    def test_matching_slug_returns_single_page(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=article)

        result = slug_matches_one_page_exactly(
            '/shows/workzonewithbridgetmasinga/', home_page)

        assert result == article

    def test_multiple_slug_depth(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=article)

        result = slug_matches_one_page_exactly(
            '/test/post/page/shows/workzonewithbridgetmasinga/', home_page)

        assert result == article

    def test_multiple_articles_with_same_slug_returns_none(self):
        home_page = Page.objects.get(slug='home')
        article_index_one = Page(
            title='First Index',
            slug='firstindex'
        )
        article_index_two = Page(
            title='Second Index',
            slug='secondindex'
        )
        home_page.add_child(instance=article_index_one)
        home_page.add_child(instance=article_index_two)

        article_one = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga'
        )
        article_two = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga'
        )

        article_index_one.add_child(instance=article_one)
        article_index_two.add_child(instance=article_two)

        result = slug_matches_one_page_exactly(
            '/shows/workzonewithbridgetmasinga/', home_page)

        assert result is None

    def test_no_matching_slug(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga'
        )
        home_page.add_child(instance=article)

        result = slug_matches_one_page_exactly(
            '/post/noresult/', home_page)

        assert result is None

    def test_slug_scopes_to_site(self):
        home_page = Page.objects.get(slug='home')
        article_index_one = Page(
            title='First Index',
            slug='firstindex'
        )
        article_index_two = Page(
            title='Second Index',
            slug='secondindex'
        )
        home_page.add_child(instance=article_index_one)
        home_page.add_child(instance=article_index_two)

        article_one = Page(
            title='Article One',
            slug='articleone'
        )
        article_two = Page(
            title='Article Two',
            slug='articletwo'
        )

        article_index_one.add_child(instance=article_one)
        article_index_two.add_child(instance=article_two)

        result = slug_matches_one_page_exactly(
            '/shows/articleone/', article_index_two)

        assert result is None


class SuggestPageFromMisspelledSlugTest(TestCase):

    def test_no_similar_slugs_returns_empty_array(self):
        home_page = Page.objects.get(slug='home')
        result = suggest_page_from_misspelled_slug(
            '/nosuchpage/', home_page)

        assert result == []

    def test_matching_slug_returns_page(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=article)

        result = suggest_page_from_misspelled_slug(
            '/workzonbridgetmasing/', home_page)

        assert article in result

    def test_multiple_matches_returns_best_matching_page(self):
        home_page = Page.objects.get(slug='home')
        better_matching_article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzonewithbridgetmasinga',
            live=True,
            first_published_at=datetime.now()
        )
        poorer_matching_article = Page(
            title='Bridget Masinga',
            slug='bridgetmasinga',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=better_matching_article)
        home_page.add_child(instance=poorer_matching_article)

        result = suggest_page_from_misspelled_slug(
            '/workzonbridgetmasing/', home_page)

        assert better_matching_article in result

    def test_multiple_matches_returns_max_3_top_matches(self):
        home_page = Page.objects.get(slug='home')
        match_1 = Page(
            title='Bridget Masinga',
            slug='bridgetmasinga',
            live=True,
            first_published_at=datetime.now()
        )
        match_2 = Page(
            title='Bridget Masinga1',
            slug='bridgetmasinga1',
            live=True,
            first_published_at=datetime.now()
        )
        match_3 = Page(
            title='Bridget Masinga2',
            slug='bridgetmasinga2',
            live=True,
            first_published_at=datetime.now()
        )
        match_4 = Page(
            title='Bridget Masinga3',
            slug='bridgetmasinga3',
            live=True,
            first_published_at=datetime.now()
        )
        home_page.add_child(instance=match_1)
        home_page.add_child(instance=match_2)
        home_page.add_child(instance=match_3)
        home_page.add_child(instance=match_4)

        result = suggest_page_from_misspelled_slug(
            '/bridget', home_page)

        assert len(result) == 3
