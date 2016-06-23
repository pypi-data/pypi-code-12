from django.shortcuts import redirect

from .utils import verify_browser


class BrowserVerificationMixin(object):
    unsupported_redirect = None
    unknown_redirect = None

    def get_unsupported_redirect_url(self):
        return self.unsupported_redirect

    def get_unknown_redirect_url(self):
        return self.unknown_redirect

    def get_browser_requirements(self):
        return None  # use defaults from settings

    def dispatch(self, request, *args, **kwargs):
        verify_browser(request, self.get_browser_requirements())
        response = None

        if request.browser_unknown:
            response = self.unknown_browser(request)
        elif request.browser_unsupported:
            response = self.unsupported_browser(request)
        else:
            response = super(BrowserVerificationMixin, self).dispatch(
                request, *args, **kwargs)
        return response

    def _redirect_or_default(self, url):
        if url:
            return redirect(url)
        return super(BrowserVerificationMixin, self).dispatch(
            self.request, **self.kwargs)

    def unknown_browser(self, request):
        return self._redirect_or_default(self.get_unknown_redirect_url())

    def unsupported_browser(self, request):
        return self._redirect_or_default(self.get_unsupported_redirect_url())
