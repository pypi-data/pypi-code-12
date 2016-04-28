from django.conf.urls import patterns, include, url

from .views import LinkListView, ImageListView

defaultpatterns = patterns('', (r'^uploader/', include('uploader.urls')),)

urlpatterns = patterns(
    '',
    url(r'^link_list\.js$', LinkListView.as_view()),
    url(r'^link_list-old_style\.js$', LinkListView.as_view(use_old_output_style=True)),
    url(r'^image_list\.js$', ImageListView.as_view()),
    url(r'^image_list-old_style\.js$', ImageListView.as_view(use_old_output_style=True)),
)

# for the admin
urlpatterns += patterns(
    'uploader.views',
    url(r'^all/$', "all_files", name="uploader-all"),
    url(r'^thumbnail/(\d+)/(\d+)x(\d+)/$', "create_thumbnail", name="uploader-create-thumbnail")
)
