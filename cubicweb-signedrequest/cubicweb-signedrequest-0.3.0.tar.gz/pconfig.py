"""cubicweb-signedrequest pyramid_cubiweb integration module

"""
import logging

from zope.interface import implementer
from pyramid.authentication import IAuthenticationPolicy

from cubicweb import AuthenticationError
from cubes.signedrequest.tools import (hash_content, build_string_to_sign,
                                       authenticate_user,
                                       get_credentials_from_headers)

logger = logging.getLogger(__name__)

def body_hash_tween_factory(handler, registry):
    """pyramid tween that add a body_hash attribute to the request with
    the md5 sum of the body. This tween must be insterted before any 
    body rewrite logic, otherwise we cannot check request's signature"""

    def body_hash(request):
        "compute and attach the md5 sum of the body of a request"
        # code to be executed for each request before
        # the actual application code goes here
        request.body_hash = hash_content(request.body_file_seekable)
        request.body_file_seekable.seek(0)
        return handler(request)

    return body_hash


@implementer(IAuthenticationPolicy)
class SignedRequestAuthPolicy(object):
    """A pyramid AuthenticationPolicy to allow authentication via a valid
    Authentication header.

    """
    headers_to_sign = ('Content-MD5', 'Content-Type', 'Date')

    def unauthenticated_userid(self, request):
        return None

    def authenticated_userid(self, request):
        logger.debug('authentication by %s', self.__class__.__name__)
        try:
            credentials = get_credentials_from_headers(request, request.body_hash)
        except AuthenticationError:
            credentials = None
        if credentials is None:
            return
        try:
            userid, signature = credentials.split(':', 1)
        except ValueError:
            logger.warning('authentication failure: invalid credentials')
            return
        repo = request.registry['cubicweb.repository']
        signed_content = build_string_to_sign(request)
        with repo.internal_cnx() as cnx:
            user_eid = authenticate_user(cnx, userid, signed_content, signature)
        return user_eid

    def effective_principals(self, request):
        return ()

    def remember(self, request, principals, **kw):
        return ()

    def forget(self, request):
        return ()
