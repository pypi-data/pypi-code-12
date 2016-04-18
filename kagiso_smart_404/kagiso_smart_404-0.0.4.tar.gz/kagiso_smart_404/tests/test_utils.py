from django.test import TestCase

from wagtail.wagtailcore.models import Page

from ..utils import determine_if_slug_matches_one_page_exactly, suggest_page_from_misspelled_slug


class DetermineIfSlugMatchesOnePageExactlyTest(TestCase):

    def test_matching_slug_returns_single_page(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        home_page.add_child(instance=article)

        result = determine_if_slug_matches_one_page_exactly(
            '/shows/workzone-with-bridget-masinga/', home_page)

        assert result == article

    def test_multiple_slug_depth(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        home_page.add_child(instance=article)

        result = determine_if_slug_matches_one_page_exactly(
            '/test/post/page/shows/workzone-with-bridget-masinga/', home_page)

        assert result == article

    def test_multiple_articles_with_same_slug(self):
        home_page = Page.objects.get(slug='home')
        article_index_one = Page(
            title='First Index',
            slug='first-index'
        )
        article_index_two = Page(
            title='Second Index',
            slug='first-index'
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

        result = determine_if_slug_matches_one_page_exactly(
            '/shows/workzone-with-bridget-masinga/', home_page)

        assert result is None

    def test_no_matching_slug(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        home_page.add_child(instance=article)

        result = determine_if_slug_matches_one_page_exactly(
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
            slug='first-index'
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

        result = determine_if_slug_matches_one_page_exactly(
            '/shows/article-one/', article_index_two)

        assert result is None


class SuggestPageFromMisspelledSlugTest(TestCase):

    def test_no_similar_slugs_returns_none(self):
        result = suggest_page_from_misspelled_slug(
            '/no-such-page/', None)
        assert result is None

    def test_matching_slug_returns_page(self):
        home_page = Page.objects.get(slug='home')
        article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        home_page.add_child(instance=article)

        result = suggest_page_from_misspelled_slug(
            '/workzon-bridget-masing/', home_page)

        assert article in result

    def test_multiple_matches_returns_best_matching_page(self):
        home_page = Page.objects.get(slug='home')
        better_matching_article = Page(
            title='Workzone with Bridget Masinga',
            slug='workzone-with-bridget-masinga'
        )
        poorer_matching_article = Page(
            title='Bridget Masinga',
            slug='bridget-masinga'
        )
        home_page.add_child(instance=better_matching_article)
        home_page.add_child(instance=poorer_matching_article)

        result = suggest_page_from_misspelled_slug(
            '/workzon-bridget-masing/', home_page)

        assert better_matching_article in result
