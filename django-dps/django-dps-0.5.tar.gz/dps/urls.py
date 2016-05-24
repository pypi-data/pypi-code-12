from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^process/(?P<token>.*)$', views.process_transaction, {},
        'dps_process_transaction'),
    url(r'^result/(?P<token>.*)$', views.transaction_result, {},
        'dps_transaction_result'),
)
