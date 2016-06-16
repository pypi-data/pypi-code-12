# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse


CALLBACK_NAME = 'AUTH0_CALLBACK_URL'
AUTH0_CALLBACK = reverse('django.auth0.views.auth_callback')
AUTH0_CALLBACK_URL = getattr(settings, CALLBACK_NAME, AUTH0_CALLBACK)
