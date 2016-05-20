import unittest

from requests import Response
from requests.exceptions import RequestException

from docido_sdk.crawler import Retry
from docido_sdk.toolbox.rate_limits import teb_retry, DEFAULT_RETRY


class LambdaCrawlerException(Exception):
    def __init__(self, response):
        self.response = response
        super(LambdaCrawlerException, self).__init__()


class TestRateLimitsHandling(unittest.TestCase):
    def test_unknown_exception_ignored(self):
        @teb_retry(exc=LambdaCrawlerException,
                   when=dict(response__status_code=429),
                   delay='response__headers__Retry-After')
        def _():
            raise Exception('Ignored')
        with self.assertRaises(Exception) as exc:
            _()
        self.assertEquals(exc.exception.message, 'Ignored')

    def test_unmet_condition_ignored(self):
        @teb_retry(exc=LambdaCrawlerException,
                   when=dict(response__status_code=429),
                   delay='response__headers__Retry-After')
        def _():
            r = Response()
            r.status_code = 200
            raise LambdaCrawlerException(r)
        with self.assertRaises(LambdaCrawlerException) as exc:
            _()
        self.assertEqual(
            exc.exception.response.status_code,
            200
        )

    def test_retry_delay_provided(self):
        @teb_retry(exc=LambdaCrawlerException,
                   when=dict(response__status_code=429),
                   delay='response__headers__Retry-After')
        def _():
            r = Response()
            r.status_code = 429
            r.headers = {'Retry-After': 3}
            raise LambdaCrawlerException(r)
        with self.assertRaises(Retry) as exc:
            _()
        self.assertEquals(
            exc.exception.countdown,
            3
        )

    def test_retry_delay_missing(self):
        @teb_retry(exc=LambdaCrawlerException,
                   when=dict(response__status_code=429),
                   delay='response__headers__Retry-After')
        def _():
            r = Response()
            r.status_code = 429
            raise LambdaCrawlerException(r)
        with self.assertRaises(Retry) as exc:
            _()
        self.assertEquals(
            exc.exception.countdown,
            DEFAULT_RETRY
        )
        self.assertEquals(
            exc.exception.kwargs,
            dict(attempt=1)
        )

    def test_incr_attempt(self):
        @teb_retry(exc=LambdaCrawlerException,
                   when=dict(response__status_code=429),
                   delay='response__headers__Retry-After')
        def _(**kwargs):
            r = Response()
            r.status_code = 429
            raise LambdaCrawlerException(r)
        with self.assertRaises(Retry) as exc:
            _(teb_retry_attempt=41)
        self.assertEquals(
            exc.exception.kwargs,
            dict(attempt=42)
        )

    def test_no_param(self):
        @teb_retry()
        def _():
            r = Response()
            r.status_code = 429
            r.headers['Retry-After'] = 7
            raise RequestException(response=r)
        with self.assertRaises(Retry) as exc:
            _()
        self.assertEqual(
            exc.exception.kwargs,
            dict(attempt=1)
        )
        self.assertEqual(exc.exception.countdown, 7)


if __name__ == '__main__':
    unittest.main()
