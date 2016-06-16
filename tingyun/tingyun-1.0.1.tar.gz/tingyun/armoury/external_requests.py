
"""this module is defined to detect the requests module
"""

import logging
from tingyun.armoury.ammunition.external_tracker import wrap_external_trace, process_cross_trace

console = logging.getLogger(__name__)


def detect_requests_request(module):
    """
    :param module:
    :return:
    """
    def request_url(method, url, *args, **kwargs):
        """
        """
        return url

    wrap_external_trace(module, 'request', 'requests', request_url)


def detect_requests_sessions(module):
    """
    :param module:
    :return:
    """
    def request_url(instance, method, url, *args, **kwargs):
        """
        """
        return url

    def parse_params(method, url, *args, **kwargs):
        _kwargs = kwargs
        _args = (method, url) + args

        if 'headers' in _kwargs:
            _kwargs['headers'] = process_cross_trace(_kwargs['headers'])
        else:
            _kwargs['headers'] = process_cross_trace(None)

        return _args, _kwargs

    wrap_external_trace(module, 'Session.request', 'requests', request_url, params=parse_params)

