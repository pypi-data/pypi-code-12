import logging

from jwkest.jwe import JWEException

from oic.oauth2 import by_schema
from oic.oauth2 import NoSuitableSigningKeys
from oic.oauth2 import TokenErrorResponse

from oic.utils.sdb import AccessCodeUsed
from oic.utils.sdb import ExpiredToken

from oic.utils.http_util import Response
from oic.utils.http_util import Unauthorized

from oic.v2.endpoint import Endpoint

logger = logging.getLogger(__name__)


class TokenEndpoint(Endpoint):
    def __init__(self, req_cls, resp_cls, refresh_cls=None, **kwargs):
        Endpoint.__init__(self, req_cls, resp_cls, **kwargs)
        self.refresh_access_token_request = refresh_cls
        
    def _access_token_endpoint(self, req, **kwargs):
        _sdb = self.server.sdb

        client_info = self.server.cdb[str(req["client_id"])]

        assert req["grant_type"] == "authorization_code"

        _access_code = req["code"].replace(' ', '+')
        # assert that the code is valid
        if _sdb.is_revoked(_access_code):
            return self.server.error(error="access_denied", descr="Token is revoked")

        # Session might not exist or _access_code malformed
        try:
            _info = _sdb[_access_code]
        except KeyError:
            return self.server.error_response(error="access_denied", 
                                       descr="Token is invalid")

        # If redirect_uri was in the initial authorization request
        # verify that the one given here is the correct one.
        if "redirect_uri" in _info:
            try:
                assert req["redirect_uri"] == _info["redirect_uri"]
            except AssertionError:
                return self.server.error_response(error="access_denied",
                                   descr="redirect_uri mismatch")

        logger.debug("All checks OK")

        issue_refresh = False
        if "issue_refresh" in kwargs:
            issue_refresh = kwargs["issue_refresh"]

        permissions = _info.get('permission', ['offline_access']) or [
            'offline_access']
        if 'offline_access' in _info[
            'scope'] and 'offline_access' in permissions:
            issue_refresh = True

        try:
            _tinfo = _sdb.upgrade_to_token(_access_code,
                                           issue_refresh=issue_refresh)
        except AccessCodeUsed as err:
            logger.error("%s" % err)
            # Should revoke the token issued to this access code
            _sdb.revoke_all_tokens(_access_code)
            return self.server.error_response(error="access_denied", descr="%s" % err)

        if "openid" in _info["scope"]:
            userinfo = self.userinfo_in_id_token_claims(_info)
            # _authn_event = _info["authn_event"]
            try:
                _idtoken = self.sign_encrypt_id_token(
                    _info, client_info, req, user_info=userinfo)
            except (JWEException, NoSuitableSigningKeys) as err:
                logger.warning(str(err))
                return self.server.error_response(error="access_denied",
                                   descr="Could not sign/encrypt id_token")

            _sdb.update_by_token(_access_code, "id_token", _idtoken)

        # Refresh the _tinfo
        _tinfo = _sdb[_access_code]

        logger.debug("_tinfo: %s" % _tinfo)

        atr = self.respcls(**by_schema(self.respcls, **_tinfo))

        logger.info("access_token_response: %s" % atr.to_dict())

        return Response(atr.to_json(), content="application/json")

    def _refresh_access_token_endpoint(self, req, **kwargs):
        _sdb = self.server.sdb
        _log_debug = logger.debug

        client_id = str(req['client_id'])
        client_info = self.server.cdb[client_id]

        assert req["grant_type"] == "refresh_token"
        rtoken = req["refresh_token"]
        try:
            _info = _sdb.refresh_token(rtoken, client_id=client_id)
        except ExpiredToken:
            return self.server.error_response(error="access_denied",
                               descr="Refresh token is expired")

        if "openid" in _info["scope"] and "authn_event" in _info:
            userinfo = self.userinfo_in_id_token_claims(_info)
            try:
                _idtoken = self.sign_encrypt_id_token(
                    _info, client_info, req, user_info=userinfo)
            except (JWEException, NoSuitableSigningKeys) as err:
                logger.warning(str(err))
                return self.server.error_response(error="access_denied",
                                   descr="Could not sign/encrypt id_token")

            sid = _sdb.access_token.get_key(rtoken)
            _sdb.update(sid, "id_token", _idtoken)

        _log_debug("_info: %s" % _info)

        atr = self.respcls(**by_schema(self.respcls, **_info))

        logger.info("access_token_response: %s" % atr.to_dict())

        return Response(atr.to_json(), content="application/json")

    def token_endpoint(self, request="", authn=None, dtype='urlencoded',
                       **kwargs):
        """
        This is where clients come to get their access tokens

        :param request: The request
        :param authn: Authentication info, comes from HTTP header
        :returns:
        """
        logger.debug("- token -")
        logger.info("token_request: %s" % request)

        req = self.reqcls().deserialize(request, dtype)

        if 'state' in req:
            if self.server.sdb[req['code']]['state'] != req['state']:
                err = TokenErrorResponse(error="unauthorized_client")
                return Unauthorized(err.to_json(), content="application/json")

        if "refresh_token" in req:
            req = self.refresh_access_token_request().deserialize(request, 
                                                                  dtype)

        logger.debug("%s: %s" % (req.__class__.__name__, req))

        try:
            client_id = self.server.client_authn(self, req, authn)
            msg = ''
        except Exception as err:
            msg = "Failed to verify client due to: {}".format(err)
            logger.error(msg)
            client_id = ""

        if not client_id:
            err = TokenErrorResponse(error="unauthorized_client",
                                     error_description=msg)
            return Unauthorized(err.to_json(), content="application/json")

        if "client_id" not in req:  # Optional for access token request
            req["client_id"] = client_id

        if isinstance(req, self.reqcls):
            try:
                return self._access_token_endpoint(req, **kwargs)
            except JWEException as err:
                return self.server.error_response_response("invalid_request",
                                            descr="%s" % err)

        else:
            return self._refresh_access_token_endpoint(req, **kwargs)
