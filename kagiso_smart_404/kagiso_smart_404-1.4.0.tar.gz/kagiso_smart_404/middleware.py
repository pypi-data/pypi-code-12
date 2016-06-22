import logging

from .constants import TRACKING_QUERY_STRING_KEY, TRACKING_QUERY_STRING_VALUE


logger = logging.getLogger('django')


class SmartRedirectMetricsMiddleware:

    def process_request(self, request):
        query_string = request.GET.get(TRACKING_QUERY_STRING_KEY)

        if query_string == TRACKING_QUERY_STRING_VALUE:
            logger.info('count#smart_404.suggested_page.clicked=1')
