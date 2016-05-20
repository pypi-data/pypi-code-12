import unittest

from docido_sdk.crawler import *


class TestCrawlersErrors(unittest.TestCase):
    def test_crawler_error(self):
        e = CrawlerError('foo')
        self.assertIsInstance(e, DocidoError)
        self.assertEqual(e.message, 'foo')

    def test_oauth_token_expired_error(self):
        e = OAuthTokenExpiredError('foo')
        self.assertIsInstance(e, CrawlerError)
        self.assertEqual(e.message, 'foo')

    def test_oauth_token_permanent_error(self):
        e = OAuthTokenPermanentError('foo')
        self.assertIsInstance(e, CrawlerError)
        self.assertEqual(e.message, 'foo')

    def test_oauth_token_refresh_required_error(self):
        e = OAuthTokenRefreshRequiredError('foo')
        self.assertIsInstance(e, CrawlerError)
        self.assertEqual(e.message, 'foo')

    def test_retry(self):
        r = Retry()
        self.assertEqual(r.traceback, None)
        try:
            raise Exception('foo')
        except Exception:
            r = Retry()
            self.assertIsNotNone(r.traceback)


if __name__ == '__main__':
    pass
