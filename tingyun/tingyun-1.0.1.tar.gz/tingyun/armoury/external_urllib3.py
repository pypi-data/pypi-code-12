
"""

"""

from tingyun.armoury.ammunition.external_tracker import wrap_external_trace, process_cross_trace


# def detect(module):
#
#     def url_request(request, method, url, *args, **kwargs):
#         return url
#
#     def parse_params(method, url, fields=None, headers=None, **urlopen_kw):
#         return method, url, fields, headers, urlopen_kw
#
#     wrap_external_trace(module, 'RequestMethods.request', 'urllib3', url_request)


def detect(module):
    """
    """
    def url_url_open(instance, method, url, *args, **kwargs):
        return url

    def parse_params(method, url, redirect=True, **kw):
        _args = (method, url)
        _kwargs = kw

        if not kw:
            _kwargs = {}

        _kwargs["redirect"] = redirect
        _kwargs["headers"] = process_cross_trace(_kwargs.get("headers", None))

        return _args, _kwargs

    wrap_external_trace(module, 'PoolManager.urlopen', 'urllib3', url_url_open, params=parse_params)
