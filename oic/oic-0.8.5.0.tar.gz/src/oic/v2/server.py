import logging

from future.backports.urllib.parse import urlparse
from oic.utils.http_util import Response

from oic.oauth2 import ParseError, ErrorResponse
from oic.oauth2.base import PBase
from oic.oic import message
from oic.v2.authorization import Authorization

logger = logging.getLogger(__name__)


class EndPoint(object):
    name = ''

    def __init__(self, reqcls=None, **kwargs):
        self.reqcls = reqcls
        self.server = None

    def parse_request(self, *args, **kwargs):
        pass

    def endpoint(self, *args, **kwargs):
        pass

    def register(self, srv):
        setattr(srv, 'parse_{}_request'.format(self.name), self.parse_request)
        setattr(srv, '{}_endpoint'.format(self.name), self.endpoint)
        self.server = srv


class Server(PBase):
    def __init__(self, config, ca_certs=None, verify_ssl=True, keyjar=None):
        PBase.__init__(self, ca_certs=ca_certs, verify_ssl=verify_ssl,
                       keyjar=keyjar)

        self.endpoints = {}
        for endp, _conf in config['endpoints'].items():
            _endp = endp(**_conf)
            _endp.register(self)

    @staticmethod
    def error_response(error, descr=None):
        response = ErrorResponse(error=error, error_description=descr)
        return Response(response.to_json(), content="application/json",
                        status="400 Bad Request")

    def parse_request(self, request, data, sformat, client_id=None):
        if sformat == "json":
            request = request().from_json(data)
        elif sformat == "jwt":
            request = request().from_jwt(data, keyjar=self.keyjar)
        elif sformat == "urlencoded":
            if '?' in data:
                parts = urlparse(data)
                scheme, netloc, path, params, query, fragment = parts[:6]
            else:
                query = data
            request = request().from_urlencoded(query)
        else:
            raise ParseError("Unknown package format: '%s'" % sformat,
                             request)

        # get the verification keys
        if client_id:
            keys = self.keyjar.verify_keys(client_id)
            sender = client_id
        else:
            try:
                keys = self.keyjar.verify_keys(request["client_id"])
                sender = request['client_id']
            except KeyError:
                keys = None
                sender = ''

        logger.debug("verify keys: {}".format(keys))
        request.verify(key=keys, keyjar=self.keyjar, sender=sender)
        return request


if __name__ == '__main__':
    conf = {
        'endpoints': {
            Authorization: {'reqcls': message.AuthorizationRequest}
        }
    }

    srv = Server(conf)

    _msg = message.AuthorizationRequest(
        response_type='code', scope='openid',
        redirect_uri='https://rp.example.com/cb',
        client_id='client_id'
    )

    areq = srv.parse_authorization_request(query=_msg.to_urlencoded())

    print(areq)
