from .utils import verify_browser


class BrowserVerificationMiddleware(object):

    def process_request(self, request):
        verify_browser(request)
