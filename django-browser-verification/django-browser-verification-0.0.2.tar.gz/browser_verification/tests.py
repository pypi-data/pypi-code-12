from django.test import RequestFactory, SimpleTestCase
from django.views.generic import TemplateView

from .mixins import BrowserVerificationMixin


class TestView(BrowserVerificationMixin, TemplateView):

    def get(self, request):
        return request


class BrowserVerificationTest(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def try_user_agent(self, agent):
        request = self.factory.get("/test/", HTTP_USER_AGENT=agent)
        response = TestView.as_view()(request)
        self.assertEqual(response.browser_unsupported, False)
        self.assertEqual(response.browser_unknown, False)

    def testBrowserAcceptedEdge(self):
        self.try_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246")

    def testBrowserAcceptedIE(self):
        self.try_user_agent("Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko")

    def testBrowserAcceptedChrome(self):
        self.try_user_agent("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2228.0 Safari/537.36")

    def testBrowserAcceptedFirefox(self):
        self.try_user_agent("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/47.1")

    def testBrowserAcceptedSafari(self):
        self.try_user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/9.0.3 Safari/7046A194A")

    def testBrowserOutdated(self):
        request = self.factory.get(
            "/test/",
            HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/25.0.2228.0 Safari/537.36"
        )
        response = TestView.as_view()(request)
        self.assertEqual(response.browser_unsupported, True)
        self.assertEqual(response.browser_unknown, False)

    def testBrowserUnknown(self):
        request = self.factory.get(
            "/test/",
            HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Cheeto/41.0.2228.0 Safari/537.36"
        )
        response = TestView.as_view()(request)
        self.assertEqual(response.browser_unsupported, True)

    def testBrowserLockout(self):
        request = self.factory.get(
            "/test/",
            HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        )

        class LockoutView(TestView):
            unsupported_redirect = "/update/"

        response = LockoutView.as_view()(request)
        self.assertEqual(response.status_code, 302)
