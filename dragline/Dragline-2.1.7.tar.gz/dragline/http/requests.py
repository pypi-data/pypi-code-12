from __future__ import absolute_import
from requests.compat import urlencode, urldefrag
import socket
from hashlib import sha1
import requests
from requests.structures import CaseInsensitiveDict
import json
import types
import sys
import six
from dragline import runtime

try:
    from requests.packages import urllib3
    urllib3.disable_warnings()
except:
    pass
socket.setdefaulttimeout(300)


class RequestError(Exception):
    pass


class Request(object):

    """
    :param url: URL to send.
    :param method: HTTP method to use.
    :param callback: name of the function to call after url is downloaded.
    :param meta:  A dict that contains arbitrary metadata for this request.
    :param headers: dictionary of headers to send.
    :param files: dictionary of {filename: fileobject} files to multipart upload.
    :param data: the body to attach to the request. If a dictionary is provided, form-encoding will take place.
    :param json: json for the body to attach to the request (if data is not specified).
    :param params: dictionary of URL parameters to append to the URL.
    :param auth: Auth handler or (user, pass) tuple.
    :param cookies: dictionary or CookieJar of cookies to attach to this request.
    :param timeout: (optional) How long to wait for the server to send
        data before giving up, as a float, or a tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Set to True by default.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to the URL of
        the proxy.
    :param stream: (optional) whether to immediately download the response
        content. Defaults to ``False``.
    :param verify: (optional) if ``True``, the SSL cert will be verified.
        A CA_BUNDLE path can also be provided.
    :param cert: (optional) if String, path to ssl client cert file (.pem).
        If Tuple, ('cert', 'key') pair.
    """
    callback = None
    meta = None
    dont_filter = False
    retry = 0

    def __init__(self, url, method=None, callback=None, meta=None, headers=None, files=None, data=None, json=None,
                 params=None, auth=None, cookies=None, timeout=None, allow_redirects=None, proxies=None, stream=None,
                 verify=None, cert=None, dont_filter=None):
        args = dict(url=url, method=method, headers=headers, files=files, data=data, json=json, params=params,
                    auth=auth, cookies=cookies, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies,
                    stream=stream, verify=verify, cert=cert)
        self.request_args = {k: v for k, v in args.items() if v is not None}
        if callback is not None:
            self.callback = callback
        if meta is not None:
            self.meta = meta
        if dont_filter:
            self.dont_filter = True

    def __getstate__(self):
        d = self.__dict__.copy()
        if not isinstance(d['callback'], six.string_types):
            d['callback'] = self.callback.__name__
        return d

    def __setstate__(self, d):
        if 'callback' in d and isinstance(d['callback'], six.string_types):
            d['callback'] = getattr(runtime.spider, d['callback'])
        self.__dict__ = d

    def __repr__(self):
        return "<%s>" % self.get_unique_id()

    def __str__(self):
        return self.get_unique_id()

    def __usha1(self, x):
        """sha1 with unicode support"""
        if six.PY3 or isinstance(x, unicode):
            return sha1(x.encode('utf-8')).hexdigest()
        else:
            return sha1(x).hexdigest()

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            return self.request_args[name]
        raise e

    def get_args(self, keys=None):
        args = runtime.settings.DEFAULT_REQUEST_ARGS.copy()
        args.update(self.request_args)
        if args['method'] is None:
            if any((args['data'], args['json'])):
                args['method'] = "POST"
            else:
                args['method'] = "GET"
        # if 'timeout' not in args:
        #    args['timeout'] = max(self.settings.DELAY, self.settings.TIMEOUT)
        for i in args:
            if callable(args[i]):
                args[i] = args[i]()
        if keys:
            return {k: args[k] for k in keys}
        return args

    def send(self):
        """
        This function sends HTTP requests.

        :returns: response
        :rtype: :class:`dragline.http.Response`
        :raises: :exc:`dragline.http.RequestError`: when failed to fetch contents

        >>> req = Request("http://www.example.org")
        >>> response = req.send()
        >>> print response.headers['status']
        200

        """
        try:
            response = runtime.request_processor.get_response(**self.get_args())
            response.meta = self.meta
            return response
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            exc_class, exc, tb = sys.exc_info()
            new_exc = RequestError("Failed to send Request on %s: %s" % (self, exc))
            six.reraise(new_exc.__class__, new_exc, tb)

    def get_unique_id(self, hashing=False):
        keys = ["method", "url", "data", "params", "json"]
        args = self.get_args(keys)
        args["url"] = urldefrag(args["url"])[0]
        request = ":".join(args[k] for k in keys[:2])
        if args["params"]:
            request += "?" + self._encode_params(args["params"])
        body = None
        if args["json"]:
            body = json.dumps(args["json"])
        elif args["data"]:
            body = self._encode_params(args["data"])
        if body:
            request += ":" + body
        if hashing:
            return self.__usha1(request)
        else:
            return request

    @staticmethod
    def _encode_params(data):
        """Encode parameters in a piece of data.

        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """
        if data is None:
            return ''
        elif isinstance(data, six.string_types):
            return data
        elif hasattr(data, 'read'):
            return data
        elif hasattr(data, '__iter__'):
            result = []
            for k, vs in sorted(CaseInsensitiveDict(data).lower_items()):
                if isinstance(vs, six.string_types) or not hasattr(vs, '__iter__'):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (k.encode('utf-8') if isinstance(k, str) else k,
                             v.encode('utf-8') if isinstance(v, str) else v))
            return urlencode(result, doseq=True)
        else:
            return data


class RequestProcessor(object):
    def get_response(self, **kwargs):
        session = requests.Session()
        response = session.request(**kwargs)

        if response.encoding == 'ISO-8859-1' and 'ISO-8859-1' not in response.headers.get('Content-Type', ''):
                response.encoding = response.apparent_encoding
        response.cookies = session.cookies
        return Response(response)

    def put_response(self, response):
        del response

    def clear(self):
        pass


class Response(requests.Response):
    """The :class:`Response <Response>` object, which contains a
    server's response to an HTTP request.
    """

    __attrs__ = [
        '_content',
        'status_code',
        'headers',
        'url',
        'history',
        'encoding',
        'reason',
        'cookies',
        'elapsed',
        'request',
        'meta'
    ]

    meta = None

    def __init__(self, response=None):
        if isinstance(response, requests.Response):
            self.__dict__ = response.__dict__

    def __len__(self):
        if 'content-length' in self.headers:
            return int(self.headers['content-length'])
        return self.raw.tell()

    @property
    def body(self):
        return self.content

    @property
    def status(self):
        return self.status_code
