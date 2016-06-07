import logging

from future.backports.urllib.parse import urlparse

from oic.v2.endpoint import Endpoint

logger = logging.getLogger(__name__)


class Authorization(Endpoint):
    name = 'authorization'

    def __init__(self, req_cls, resp_cls, **kwargs):
        Endpoint.__init__(self, req_cls, resp_cls, **kwargs)

    def parse_request(self, url=None, query=None, keys=None):
        if url:
            parts = urlparse(url)
            scheme, netloc, path, params, query, fragment = parts[:6]

        return self.server.parse_request(self.req_cls, query, "urlencoded")

    def endpoint(self, request="", cookie=None, **kwargs):
        req = self.parse_request(query=request)


