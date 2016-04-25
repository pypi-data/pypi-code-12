from django.conf.urls.defaults import *

urlpatterns = patterns('',
        (r'^$', 'mauveinternet.ordering.views.orders_new'),
        (r'^all$', 'mauveinternet.ordering.views.orders_all'),
        url(r'^(?P<code>[0-9]+)/$', 'mauveinternet.ordering.views.view_order', name='view-order'),
        url(r'^(?P<code>[0-9]+)/view-item', 'mauveinternet.ordering.views.view_order_item', name='view-order-item'),
)
