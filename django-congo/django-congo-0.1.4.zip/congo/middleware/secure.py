# -*- coding: utf-8 -*-
from congo.conf import settings
from django.http.response import HttpResponseRedirect

class SecureMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not settings.CONGO_SSL_ENABLED:
            return None

        # uwaga! POST tracimy po przekierowaniu!

        url = request.build_absolute_uri()
        if any(pattern.search(url) for pattern in settings.CONGO_IGNORABLE_SSL_URLS):
            return None

        secure_required = getattr(view_func, 'secure', False)
        if secure_required or request.is_admin_backend:
            if not request.is_secure():
                url = url.replace('http://', 'https://')
#                 return HttpResponsePermanentRedirect(url)
                return HttpResponseRedirect(url)
        elif secure_required is False:
            if request.is_secure():
                url = request.build_absolute_uri()
                url = url.replace('https://', 'http://')
#                 return HttpResponsePermanentRedirect(url)
                return HttpResponseRedirect(url)

        return None
