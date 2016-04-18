"""
Provides a set of Exception classes a crawler may raise when it is
not possible to consume source API because of OAuth-related issues.
"""

import sys

from .. core import DocidoError


class CrawlerError(DocidoError):
    """Common base exception class for crawl issues"""
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          reason for error.
        """
        super(CrawlerError, self).__init__(message)


class OAuthTokenExpiredError(CrawlerError):
    """Exception class used to notify crawler manager when
    the OAuth token of an account has expired, and needs to be refreshed
    thru Docido front application.
    """
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          the error message returned by source API.
        """
        super(OAuthTokenExpiredError, self).__init__(message)


class OAuthTokenPermanentError(CrawlerError):
    """Exception class used to notify crawler manager when
    the OAuth token of an account has been revoked.
    """
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          the error message returned by source API.
        """
        super(OAuthTokenPermanentError, self).__init__(message)


class OAuthTokenRefreshRequiredError(CrawlerError):
    """Exception class used to notify crawler manager when
    the OAuth token of an account has expired or will expire
    shortly, and need to be refreshed programmaticaly.
    """
    def __init__(self, message=None):
        """
        @param message: optional printable object providing
          the error message returned by source API.
        """
        super(OAuthTokenRefreshRequiredError, self).__init__(message)


class Retry(Exception):
    def __init__(self, kwargs=None, countdown=None, exc=None,
                 eta=None, max_retries=None):
        """Retry the task.

        This exception can be raised by a crawl task to tell the framework
        to retry it later on.

        :param kwargs:
          task keyword arguments to retry with
        :param countdown:
          time in seconds to delay the retry for.
        :param exc:
          custom exception to report when the max restart limit exceeded.
        :param eta:
          explicit time and date to run the retry for. Must be
          a :class:`~datetime.datetime` instance.
        :param max_retries:
          if set, overrides the default retry limit
        """
        self.kwargs = kwargs
        self.exc = exc
        self.countdown = countdown
        self.eta = eta
        self.max_retries = max_retries
        self.traceback = sys.exc_info()[2]

    def __eq__(self, other):
        return self.kwargs == other.kwargs and \
            self.exc == other.exc and \
            self.countdown == other.countdown and \
            self.eta == other.eta and \
            self.max_retries == other.max_retries

    def __ne__(self, other):
        return not self.__eq__(other)
