from django.contrib.sitemaps import Sitemap
from wagtail.wagtailcore.models import Page


class KagisoSitemap(Sitemap):
    # Django uses `limit` for paging, although it isn't documented
    # Default is 50 000 which results in timeouts for us
    limit = 500
    changefreq = 'never'
    priority = '0.7'

    def items(self):
        pages = Page.objects \
            .live() \
            .public() \
            .exclude(slug='root') \
            .order_by('path')
        return pages

    def lastmod(self, obj):
        return obj.first_published_at

    def location(self, obj):
        # HACK: Django appends url to start of location using Django Sites,
        # which isn't aware of Wagtail Sites or our multitenancy,
        # so urls look like http://jac.127.0.0.1.xip.io:8000http://ecr.127.0.0.1.xip.io:8000/shows/  # noqa
        # Simply rely on Wagtail for correct full url,
        # and insert space as delimiter between urls
        # so first url can be stripped out in custom template
        return ' ' + obj.url
