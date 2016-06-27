from wagtail.wagtailcore.models import Page


def pg_full_text_search(search_query, root_page):
    root_path = root_page.path
    root_path_len = len(root_path)
    search_query = _prepare_query(search_query)

    sql = ("WITH QUERY AS ("  # noqa
            "SELECT to_tsquery('english', %s) AS tsquery "  # noqa
            ") "  # noqa
            "SELECT p.*, "  # noqa
            "ts_headline('english', p.title, query.tsquery) AS headline, "  # noqa
            "ts_rank_cd(to_tsvector('english', p.title), query.tsquery) AS rank "  # noqa
            "FROM wagtailcore_page p, query "  # noqa
            "WHERE substring(path for %s) = %s AND to_tsvector('english', p.title) @@ query.tsquery AND p.live = true "  # noqa
            "ORDER BY rank DESC, first_published_at DESC")  # noqa

    return Page.objects.raw(sql, [search_query, root_path_len, root_path])


def _prepare_query(query):
    # Ampersands are special characters used for PG full text search (the AND operator) # noqa
    query = query.replace('&', '')

    # Multiple terms must have AND/OR/NOT, so join the terms with AND
    # http://www.postgresql.org/docs/9.4/static/textsearch-intro.html#TEXTSEARCH-MATCHING
    query_list = query.split()
    query = ' & '.join(query_list)

    return query
