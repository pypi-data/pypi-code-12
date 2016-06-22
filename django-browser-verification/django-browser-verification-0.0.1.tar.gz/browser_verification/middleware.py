from .utils import verify_browser


class BrowserVerificationMiddleware(object):

    def process_request(request):
        verify_browser(request)
