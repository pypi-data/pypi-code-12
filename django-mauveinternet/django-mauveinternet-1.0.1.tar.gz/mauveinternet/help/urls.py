from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
      url(r'^ajax/(?P<slug>[\w-]+)$', 'mauveinternet.help.views.ajax_help', name='ajax-help'),
      url(r'^quick/(?P<slug>[\w-]+)$', 'mauveinternet.help.views.quick_help', name='quick-help'),
)
