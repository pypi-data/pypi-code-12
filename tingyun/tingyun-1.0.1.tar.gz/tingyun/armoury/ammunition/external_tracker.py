
"""

"""

import logging
import random
import time

from tingyun.armoury.ammunition.timer import Timer
from tingyun.logistics.warehouse.external_node import ExternalNode
from tingyun.armoury.ammunition.tracker import current_tracker
from tingyun.logistics.basic_wrapper import FunctionWrapper, wrap_object

console = logging.getLogger(__name__)


class ExternalTrace(Timer):
    """define the external trace common api.

    """
    def __init__(self, tracker, library, url, params=None):
        super(ExternalTrace, self).__init__(tracker)

        self.library = library
        self.url = url.split('?')[0]
        self.params = self.parse_request_params(url, params)
        self.protocol = "http"
        self.protocol = "https" if "https" in url else self.protocol
        self.protocol = "thrift" if "thrift" in url else self.protocol

        signed_param = []
        for p in self.params:
            if tracker.settings and p in tracker.settings.external_url_params_captured.get(self.url, ""):
                signed_param.append("%s=%s&" % (p, self.params[p]))

        if 0 != len(signed_param):
            self.url = "%s?%s" % (self.url, ''.join(signed_param).rstrip('&'))

    def parse_request_params(self, url, post_data):
        """ Note: some url request lib passed in the post data in different way.
        so do not support post data params capture now.
        :param url:
        :param post_data:
        :return:
        """
        params_tmp = url.split("?")
        params = params_tmp[1] if 2 == len(params_tmp) else ""
        kv_params = [p for p in params.split("&") if p.strip()]

        actual_params = {}
        for kv in kv_params:
            k, v = kv.split('=', 1)
            if not k.strip() or not v.strip():
                continue

            actual_params[k.strip()] = v.strip()

        return actual_params

    def create_node(self):
        tracker = current_tracker()
        if tracker:
            tracker.external_time = self.duration

        return ExternalNode(library=self.library, url=self.url, children=self.children, protocol=self.protocol,
                            start_time=self.start_time, end_time=self.end_time, duration=self.duration,
                            exclusive=self.exclusive)

    def terminal_node(self):
        return True


def external_trace_wrapper(wrapped, library, url, params=None):
    """
    :param params: just use for cross trace with replaced headers.
    :return:
    """

    def dynamic_wrapper(wrapped, instance, args, kwargs):
        tracker = current_tracker()
        if tracker is None:
            return wrapped(*args, **kwargs)

        _url = url
        if callable(url):
            if instance is not None:
                _url = url(instance, *args, **kwargs)
            else:
                _url = url(*args, **kwargs)

        with ExternalTrace(tracker, library, _url, kwargs):
            if not callable(params):
                return wrapped(*args, **kwargs)
            else:
                _args, _kwargs = params(*args, **kwargs)
                ret = wrapped(*_args, **_kwargs)

                try:
                    # for requests/urllib3
                    if hasattr(ret, 'headers'):
                        tracker._called_traced_data = eval(ret.headers.get("X-Tingyun-Tx-Data", '{}'))

                    # for httplib2, note: the httplib2 will trans the upper case to lower case
                    if isinstance(ret, tuple):
                        tracker._called_traced_data = eval(ret[0].get("x-tingyun-tx-data", '{}'))
                except Exception as err:
                    console.debug(err)

                return ret

    def literal_wrapper(wrapped, instance, args, kwargs):
        tracker = current_tracker()

        if tracker is None:
            return wrapped(*args, **kwargs)

        with ExternalTrace(tracker, library, url, kwargs):
            return wrapped(*args, **kwargs)

    if callable(url):
        return FunctionWrapper(wrapped, dynamic_wrapper)

    return FunctionWrapper(wrapped, literal_wrapper)


def wrap_external_trace(module, object_path, library, url, params=None):
    wrap_object(module, object_path, external_trace_wrapper, (library, url, params))


def process_cross_trace(headers):
    """
    """
    if headers is None:
        headers = {}

    tracker = current_tracker()
    if not tracker or not tracker.enabled:
        return headers

    if not tracker.settings.transaction_tracer.enabled:
        return headers

    headers['X-Tingyun-Id'] = tracker.settings.x_tingyun_id % (tracker._tingyun_id, tracker.generate_trace_id())

    return headers
