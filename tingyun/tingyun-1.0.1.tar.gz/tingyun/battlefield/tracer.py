import cgi
import logging
import threading
import time

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from tingyun.armoury.ammunition.tracker import Tracker
from tingyun.packages import six


console = logging.getLogger(__name__)
TINGYUN_TRACE_CODE_LENGTH = 16


class Tracer(Tracker):
    """
    """
    def __init__(self, application, environ, framework="Python"):
        """
        """
        Tracker.__init__(self, application, environ, framework)

        self.get_thread_name()
        script_name = environ.get('SCRIPT_NAME', "")
        path_info = environ.get('PATH_INFO', "")
        self.request_uri = environ.get("REQUEST_URI", "")
        self.referer = environ.get("HTTP_REFERER", "")
        self.browser_header_prepared = False
        self.agent_browser_code = "ty_rum.agent={id:'%s', n:'%s', a:'%s', q:'%s', tid: '%s'}"

        if self.request_uri:
            self.request_uri = urlparse.urlparse(self.request_uri)[2]
            
        if script_name or path_info:
            if not path_info:
                path = script_name
            elif not script_name:
                path = path_info
            else:
                path = script_name + path_info

            self.set_tracker_name(path, 'Uri', priority=1)

            if not self.request_uri:
                self.request_uri = path
        else:
            if self.request_uri:
                self.set_tracker_name(self.request_uri, 'Uri', priority=1)

        # get the param
        self._get_request_params(environ)
        self.calculate_queque_time(environ)
        self.process_cross_trace(environ)

    def process_cross_trace(self, environ):
        """
        :return:
        """
        if not self.enabled:
            return

        # as caller
        tingyun_id = 'HTTP_X_TINGYUN_ID'
        tingyun_headers = environ.get(tingyun_id, "")

        if not tingyun_headers:
            return

        # not the same account,skip it
        ids = tingyun_headers.split(';')
        call_tingyun_id = ids[0].split('|')[0]
        called_tingyun_id = self._tingyun_id.split('|')[0]
        if call_tingyun_id != called_tingyun_id:
            self.call_tingyun_id = ""
            console.debug("Get the invalid tingyun id %s", environ.get(tingyun_id, ""))
            return

        id_dict = dict()
        for h in ids[1:]:
            if '=' not in h:
                continue

            kv = h.split('=')
            id_dict[kv[0]] = kv[1]

        self.call_tingyun_id = ids[0]
        self.call_req_id = id_dict.get("r", "")
        self._trace_id = id_dict.get("x", "")

    def deal_response(self, status, response_headers, *args):
        """
        :param status:
        :param response_headers:
        :param args:
        :return:
        """
        try:
            self.http_status = int(status.split(' ')[0])
        except Exception as _:
            console.warning("get status code failed, status is %s", status)

    def calculate_queque_time(self, env):
        """
        :return:
        """
        # for compitable with old version with modwsgi
        queue_header = ('HTTP_X_QUEUE_START', 'mod_wsgi.request_start', 'mod_wsgi.queue_start')
        x_queque = None

        for header in queue_header:
            x_queque = env.get(header, None)
            if x_queque:
                break

        if x_queque is None:
            return

        try:
            key, value = tuple(x_queque.split('='))
            # deal value from nginx
            if 't' == key:
                self.queque_start = float(value) / 1000.0
            else:
                self.queque_start = float(value) * 1000.0
        except Exception as err:
            pass

    def _get_request_params(self, environ):
        """
        :param environ: cgi environment
        :return: referer
        """
        value = environ.get('QUERY_STRING', "")
        if value:
            params = {}

            try:
                params = urlparse.parse_qs(value, keep_blank_values=True)
            except Exception:
                try:
                    # method <parse_qs> only for backward compatibility,  method <parse_qs> new in python2.6
                    params = cgi.parse_qs(value, keep_blank_values=True)
                except Exception:
                    pass

            self.request_params.update(params)

    def get_thread_name(self):
        """
        :return: thread name
        """
        try:
            self.thread_name = threading.currentThread().getName()
        except Exception as err:
            console.info("Get thread name failed. %s", err)
            self.thread_name = "unknown"

        return self.thread_name

    def start_work(self):
        """
        :return:
        """
        self.__enter__()

    def finish_work(self, exc_type, exc_val, exc_tb, async=False):
        """
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.__exit__(exc_type, exc_val, exc_tb, async)

    def generate_agent_param(self):
        """
        :return:
        """
        duration = int((time.time() - self.start_time) * 1000)
        queque_time = self.queque_time
        guid = ""

        if self.settings and self.settings.action_tracer.action_threshold < duration:
            guid = self.generate_trace_guid()

        bids = self._settings.tingyunIdSecret.split('|')
        bid = bids[1] if len(bids) == 2 else "do-not-get-id-for-callable"
        agent_param = self.agent_browser_code % (bid, self.path, duration, queque_time, guid)

        return agent_param

    def fork_browser_js_head(self):
        """generate the head for rum
        :return:
        """
        header = b''

        if not self.settings or not self.enabled:
            return header

        if not self.settings.rum.enabled:
            return header

        if self.browser_header_prepared:
            return header

        if not self.settings.rum.script:
            return header

        agent_param = self.generate_agent_param()
        param_index = str(self.settings.rum.script).rfind('}')
        header = "<script type='text/javascript'>%s%s%s</script>" % (self.settings.rum.script[:param_index],
                                                                     agent_param,
                                                                     self.settings.rum.script[param_index:])

        # avoid some issues, just use the ascii encoding to specify the insert js script in head tag
        try:
            if six.PY2:
                header = header.encode('ascii')
            else:
                header.encode('ascii')
        except UnicodeError:
            header = b''

        self.browser_header_prepared = True if header else False

        return header
