import abc
import time

import datarobot.errors as err


class Delay(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def delay(self):
        """Must be called with no arguments, and is responsible for carrying
        out some sort of delay action
        """


class ConstantDelay(Delay):

    def __init__(self, delay_seconds):
        self.delay_seconds = delay_seconds

    def delay(self):
        time.sleep(self.delay_seconds)


class NoDelay(Delay):

    def delay(self):
        pass


class ExponentialBackoffDelay(Delay):
    """Does an exponentially increasing backoff. Note that the Retry manager
    is responsible for deciding *how many times* to retry, this just keeps
    increasing the delay time exponentially. User beware

    Parameters
    ----------
    initial : int
        The initial delay time
    growth : int
        The growth rate. Each successive delay will take ``growth`` times as
        long.
    """

    def __init__(self, initial, growth):
        self.delay_seconds = initial
        self.growth = growth

    def delay(self):
        time.sleep(self.delay_seconds)
        self.delay_seconds = self.delay_seconds * self.growth


class RetryManager(object):
    """Given an object that will execute a request, this object will handle
    any potentially necessary retries

    Parameters
    ----------
    requestor : object
        Implements a ``send_request`` method, that may possibly raise some
        exceptions which should be retried.
    n_retries : int, default 3
        The number of times to attempt to retry
    nonfatal_exceptions : tuple, optional
        The tuple of exceptions which are non-fatal on first try. This could
        be something like a timeout exception
    delay_manager : datarobot.retry.Delay object, optional
        If `None`, then the default is to use a 5 second delay between
        failure and retry
    """

    NON_FATAL_EXCEPTIONS = tuple()

    def __init__(self,
                 requestor,
                 n_retries=3,
                 nonfatal_exceptions=None,
                 delay_manager=None):
        self.requestor = requestor
        self.retries = n_retries
        self.nonfatal_exceptions = (nonfatal_exceptions or
                                    self.NON_FATAL_EXCEPTIONS)
        self.delay_manager = delay_manager or ConstantDelay(5)
        self.errors = []

    def send_request(self, **kwargs):
        return self._send_request_inner(n_retries=self.retries, **kwargs)

    def _send_request_inner(self, n_retries, **kwargs):
        if n_retries < 0:
            err_msg = self._format_errors()
            raise err.AllRetriesFailedError(err_msg)
        try:
            response = self.requestor.send_request(**kwargs)
            return response
        except self.nonfatal_exceptions as e:
            self.errors.append(e)
            self.delay_manager.delay()
            self._send_request_inner(n_retries - 1, **kwargs)

    def _format_errors(self):
        formatted_errs = ['Error {}: {}'.format(idx, repr(error))
                          for idx, error in enumerate(self.errors)]
        return '\n'.join(formatted_errs)
