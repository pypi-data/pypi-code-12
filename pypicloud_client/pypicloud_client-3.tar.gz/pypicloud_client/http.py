import furl
import logging
from random import randint
import requests
from requests.exceptions import RequestException
import time

logger = logging.getLogger(__name__)

SUCCESS_HTTP_CODE = [200, 201, 204]


class HTTPErrorCode(Exception):
    """Exception raised by a failed call on Failed HTTP Requests"""


def retry_http(call):
    """Wrapper used to retry HTTP Errors with an exponential backoff

    Args:
        call: function being wrapped

    Returns:
        the wrapped function
    """

    def _retry_http(*args, **kwargs):
        """Retry a function call when catching requests.exceptions.RequestException

        """
        last_exception = None
        multiplier = 1.5
        retry_interval = 0.5
        randomization_factor = 0.5
        total_sleep_time = 0
        # Capped to 10 seconds
        max_sleep_time = 10

        request_nb = 0
        while total_sleep_time < max_sleep_time:
            try:
                return call(*args, **kwargs)
            except HTTPErrorCode as exc:
                total_sleep_time, request_nb = exponential_backoff(exc, max_sleep_time, multiplier,
                                                                   randomization_factor, request_nb, retry_interval,
                                                                   total_sleep_time)
                last_exception = exc
            except RequestException as exc:
                total_sleep_time, request_nb = exponential_backoff(exc, max_sleep_time, multiplier,
                                                                   randomization_factor, request_nb, retry_interval,
                                                                   total_sleep_time)
                last_exception = exc
        logger.error('Max sleep time exceeded, raising exception.')
        raise last_exception

    def exponential_backoff(exc, max_sleep_time, multiplier, randomization_factor, request_nb,
                            retry_interval, total_sleep_time):
        """Implements the exponential backoff for HTTP Requests.

        Args:
            exc:
            max_sleep_time:
            multiplier:
            randomization_factor:
            request_nb:
            retry_interval:
            total_sleep_time:

        Returns:

        """
        # Inspired from https://developers.google.com/api-client-library/java/google-http-java-client/reference/
        # 1.20.0/com/google/api/client/util/ExponentialBackOff
        next_retry_sleep = (multiplier ** request_nb *
                            (retry_interval *
                             (randint(0, int(2 * randomization_factor * 1000)) / 1000 +
                              1 - randomization_factor)))
        total_sleep_time += next_retry_sleep
        request_nb += 1
        time.sleep(next_retry_sleep)
        logger.warning('Got an exception: {exc}. Slept ({retry} seconds / {total} seconds)'
                       .format(exc=exc,
                               retry=total_sleep_time,
                               total=max_sleep_time))
        return total_sleep_time, request_nb

    # Keep the doc
    if call.__doc__:
        _retry_http.__doc__ += call.__doc__

    return _retry_http


@retry_http
def request_factory(host, req_type, endpoint, headers=None, body=None, params=None, auth=None,
                    return_none_on_404=True):
    """Makes HTTP Requests

    Args:
        host (str): Host of the URL to send.
        headers: dictionary of headers to send.
        req_type (str): HTTP verb
        endpoint: Endpoint of the URL to send.
        body: the body to attach to the request.
        params: dictionary of URL parameters to append to the URL.
        auth: Auth handler or (user, pass) tuple.
        return_none_on_404: Return None if the response has status_code 404

    Returns:
        dict: The decoded response or None if status code is 204

    Raises:
        HTTPErrorCode: Request error.
    """
    # We declare the furl host here because when 'join' is called, ``fhost`` is updated
    fhost = furl.furl(host)

    if req_type == 'GET':
        response = requests.get(fhost.join(endpoint), json=body, params=params, headers=headers, auth=auth)
    elif req_type == 'POST':
        response = requests.post(fhost.join(endpoint), json=body, params=params, headers=headers, auth=auth)
    elif req_type == 'PUT':
        response = requests.put(fhost.join(endpoint), json=body, params=params, headers=headers, auth=auth)
    elif req_type == 'DELETE':
        response = requests.delete(fhost.join(endpoint), json=body, params=params, headers=headers, auth=auth)
    else:
        raise HTTPErrorCode({'request_factory': 'Unknown request type: {0}'.format(req_type)})

    if return_none_on_404 and response.status_code == 404:
        return None
    elif response.status_code not in SUCCESS_HTTP_CODE:
        raise HTTPErrorCode({
            'error': response.status_code,
            'msg': response.text,
        })
    elif response.status_code == 204:
        return
    else:
        if len(response.text) > 0:
            return response.json()
        else:
            return
