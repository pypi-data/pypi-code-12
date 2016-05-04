from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from api import ButterCms


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
    	butter = ButterCms()
        response = butter.get_sitemap()
        return response

    def location(self, item):
        return reverse('blog_post', args=[item['slug']])