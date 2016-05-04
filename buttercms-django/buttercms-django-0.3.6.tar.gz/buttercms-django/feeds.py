from datetime import datetime

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed

from api import ButterCms


class LatestPostFeed(Feed):
    title = "Latest blog posts"

    def link(self):
    	return reverse('blog_rss')

    def items(self):
    	butter = ButterCms()
        response = butter.get_posts(None)
        return response['results']

    def item_title(self, item):
        return item['title']

    def item_description(self, item):
        return item['summary']

    def item_link(self, item):
        return reverse('blog_post', args=[item['slug']])

    def item_author_name(self, item):
    	return '%s %s' % (item['author']['first_name'], item['author']['last_name'])

    def item_pubdate(self, item):
    	return datetime.strptime(item['published'], '%m/%d/%Y')

    def item_updateddate(self, item):
        return datetime.strptime(item['published'], '%m/%d/%Y')

    #TODO(jake): Subclass this to add featured images as well.


class AtomBlogPostFeed(LatestPostFeed):
    feed_type = Atom1Feed


