from django.conf.urls import url
from django.contrib.sitemaps.views import index as sitemap_index, sitemap

from .sitemaps import KagisoSitemap

sitemaps = {'kagiso': KagisoSitemap()}

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap_index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$',
        sitemap, {
            'sitemaps': sitemaps,
            'template_name': 'kagiso_sitemap/kagiso_sitemap.xml'
        }),
]
