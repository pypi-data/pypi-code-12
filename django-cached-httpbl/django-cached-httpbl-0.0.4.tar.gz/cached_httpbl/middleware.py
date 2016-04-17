"""CachedHTTPBL middleware """

import logging

from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect

from cached_httpbl.conf import settings
from cached_httpbl.api import CachedHTTPBL
from cached_httpbl.helpers import get_user_ip

if settings.CACHED_HTTPBL_USE_LOGGING:
    logger = logging.getLogger(__name__)


class CachedHTTPBLViewMiddleware(object):
    def __init__(self):
        self.redirect_url = settings.CACHED_HTTPBL_REDIRECT_URL
        self.ignore_methods = settings.CACHED_HTTPBL_IGNORE_REQUEST_METHODS

    def process_request(self, request):

        httpbl = CachedHTTPBL()
        ip = get_user_ip(request)
        request.__httpbl_result = httpbl.check_ip(ip)
        request.__httpbl_is_threat = httpbl.is_threat()
        request.__httpbl_is_suspicious = httpbl.is_suspicious()

        if request.method not in self.ignore_methods and request.__httpbl_is_threat:
            if settings.CACHED_HTTPBL_USE_LOGGING:
                logger.info(
                    'Blocked request from {0}; httpBL result: '
                    '[error: {1}, age: {2}, threat: {3}, type: {4}]'.format(ip,
                                                                            request.__httpbl_result['error'],
                                                                            request.__htpbl_result['age'],
                                                                            request.__httpbl_result['threat'],
                                                                            request.__httpbl_result['type']
                                                                            )
                )

            if self.redirect_url is not None:
                return HttpResponsePermanentRedirect(self.redirect_url)
            else:
                return HttpResponseNotFound(settings.CACHED_HTTPBL_RESPONSE_NOT_FOUND_HTML)

    def process_template_response(self, request, response):
        response.context_data['httpbl_result'] = request.__httpbl_result
        response.context_data['httpbl_is_threat'] = request.__httpbl_is_threat
        response.context_data['httpbl_is_suspicious'] = request.__httpbl_is_suspicious
        return response
