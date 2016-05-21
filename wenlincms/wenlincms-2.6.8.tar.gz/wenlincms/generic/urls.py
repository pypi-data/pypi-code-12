from __future__ import unicode_literals

from django.conf.urls import patterns, url

urlpatterns = patterns("wenlincms.generic.views",
                       url("^admin_keywords_submit/$", "admin_keywords_submit", name="admin_keywords_submit"),
                       url("^comment/$", "comment", name="comment"),
                       url(r'^comment/support/(\d+)/$', 'comment_support', name='comments-comment-support'),
                       )
