from django.db import models
""""
from import urls

def show_urls(urllist, depth=0):
    for entry in urllist:
        print "  " * depth, entry.regex.pattern
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)

show_urls(urls.urlpatterns)
"""
"""
	@name: OAthToken
	@author: exile.sas
	@date: 27/06/2016
	@licence: creative commons
"""
class OAthToken(models.Model):
	date = models.DateTimeField(auto_now_add=True)
	token = models.CharField(max_length=120)
	expire_date = models.DateTimeField(null=True, default=None)
	enable = models.BooleanField(default=True)

# end class

#class Url(models.Model):
