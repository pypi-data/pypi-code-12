from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()
# admin.site.unregister(User)


urlpatterns = patterns(
    '', (r'^accounts/', include('registration.urls')),
)

APP_LIST = ['archaeological_files_pdl', 'archaeological_files',
            'archaeological_operations', 'archaeological_context_records',
            'archaeological_warehouse', 'archaeological_finds']
for app in APP_LIST:
    # filter by activated apps?
    urlpatterns += patterns(
        '', ('', include(app + '.urls')),
    )

urlpatterns += patterns(
    '', ('', include('ishtar_common.urls')),
)

urlpatterns += patterns(
    'ishtar_common.views', url(r'^$', 'index', name='start'),
)

urlpatterns += patterns(
    '', (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns(
        '', (r'^media/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT}))
