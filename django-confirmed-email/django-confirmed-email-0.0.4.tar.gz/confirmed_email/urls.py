'''
Created on Feb 11, 2016

@author: jivan
'''
from django.conf.urls import url, patterns
from confirmed_email.views import HandleConfirmationClick

urlpatterns = patterns('',
    url(r'^confirm-email-address/(?P<uuid>.*?)$', HandleConfirmationClick.as_view(),
        name='confirmed-email-confirmation-url'
    ),
)
