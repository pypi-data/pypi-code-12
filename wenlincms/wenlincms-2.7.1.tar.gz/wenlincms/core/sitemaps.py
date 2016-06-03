# -*- coding: utf-8 -*-
# 非池 2015-06-13
from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap
from wenlincms.core.models import Displayable


class DisplayableSitemap(Sitemap):
    Sitemap.limit = 20000

    # changefreq = "weekly"

    def items(self):
        return list(Displayable.objects.url_map().values())

    # def lastmod(self, obj):
    #     return obj.updated

    def get_urls(self, **kwargs):
        return super(DisplayableSitemap, self).get_urls(**kwargs)
