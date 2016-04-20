# coding: utf-8
"""
    pyextend.network.gziphandler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend network gziphandler

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

from urllib import request, response
from gzip import GzipFile
from io import BytesIO as StringIO
import zlib

__all__ = ['build_gzip_opener', 'deflate', 'ContentEncodingHandler']


class ContentEncodingHandler(request.BaseHandler):
    """A handler to add gzip capabilities to urllib requests"""
    
    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip, deflate")
        return req

    def http_response(self, req, resp):
        old_resp = resp

        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile(
                fileobj=StringIO(resp.read()),
                mode='r'
                )

            resp = response.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg

        if resp.headers.get("content-encoding") == "deflate":
            gz = StringIO(deflate(resp.read()))
            resp = response.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg

        return resp

    https_request = http_request
    https_response = http_response


def deflate(data):
    try:
        return zlib.decompress(data, -zlib.MAX_WBITS)
    except zlib.error:
        return zlib.decompress(data)


def build_gzip_opener(https=False):
    encoding_support = ContentEncodingHandler
    return request.build_opener(encoding_support, request.HTTPHandler if not https else request.HTTPSHandler)


if __name__ == '__main__':
    url = "https://github.com/"
    opener = build_gzip_opener(https=True)
    content = opener.open(url).read()
    print(content)
