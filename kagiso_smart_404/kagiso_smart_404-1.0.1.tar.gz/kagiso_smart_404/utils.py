from wagtail.wagtailcore.models import Page


def page_slug(slug):
    # Full slug might be /news/sports/some-sports-article/
    # The page slug is therefore `some-sports-article`
    slugs = slug.split('/')

    # Remove all empty strings
    # '/news/article' => ['', 'news', 'article', '']
    slugs = list(filter(None, slugs))

    page_slug = slugs[-1]
    return page_slug


def slug_matches_one_page_exactly(slug, root_page):
    slug = page_slug(slug)
    try:
        result = Page.objects.descendant_of(root_page).get(
            slug=slug,
            live=True,
            first_published_at__isnull=False
        )
        return result
    except (Page.MultipleObjectsReturned, Page.DoesNotExist):
        return None


def suggest_page_from_misspelled_slug(slug, root_page):
    sql = '''SELECT p.*, similarity(slug, %(slug)s) AS similarity
             FROM wagtailcore_page p
             WHERE live = true
                AND first_published_at IS NOT NULL
                AND slug %% %(slug)s
             ORDER BY similarity DESC
             '''
    page = Page.objects.raw(sql, {'slug': slug})
    suggested_pages = None

    # page is currently a RawQuerySet...
    if list(page) and root_page in page[0].get_ancestors().specific():
        suggested_pages = list(page)

    return suggested_pages[:3] if suggested_pages else None
