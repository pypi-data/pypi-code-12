"""cubicweb-signedrequest tools for parsing and checking Authorization
headers

"""


import logging
from datetime import datetime, timedelta
from email.utils import parsedate
import hmac
import hashlib

from six.moves import zip

from cubicweb import AuthenticationError

try:
    from hmac import compare_digest
except ImportError:
    # python 3.3 has hmac.compare_digest, but older versions don't.
    # this version should leak less timing information than the normal string
    # equality check
    # the expectation here is that both inputs are ascii strings of the same
    # length
    def compare_digest(expected, actual):
        if len(expected) != len(actual):
            return False
        result = 0
        for (a, b) in zip(expected, actual):
            result |= ord(a) ^ ord(b)
        return result == 0

log = logging.getLogger(__name__)

HEADERS_TO_SIGN = ('Content-MD5', 'Content-Type', 'Date')


def hash_content(content):
    """compute the md5 sum of a file-like object's content
    
    Does NOT put the file's pos at the original position 
    """
    all = ''
    md5 = hashlib.md5()
    while True:
        data = content.read(4096)
        if not data:
            break
        md5.update(data)
        all += data
    return md5.hexdigest()

def get_credentials_from_headers(request, content_md5):
    """Parse the request headers to retrieve the authentication credentials

    Returns the parsed credentials as a string '<tokenid>:<signature>' where
      <tokenid> is the identifier of the authentication token (AuthToken)
      <signature> is the signature of the content of the request, which must be
                  forged using the token's secret key to authenticate
                  the user linked with the AuthToken
    """
    header = request.get_header('Authorization', None)
    if header is None:
        log.debug('SIGNED REQUEST: error header is none')
        return
    try:
        method, credentials = header.split(None, 1)
    except ValueError:
        log.debug("SIGNED REQUEST: couldn't determine method from Authorization header")
        return
    if method != 'Cubicweb':
        log.debug('SIGNED REQUEST: method is not Cubicweb')
        return
    if request.http_method() != 'GET':
        if content_md5 != request.get_header('Content-MD5'):
            log.warning('SIGNED REQUEST: wrong md5, %s != %s' % (content_md5,
                                                                 request.get_header('Content-MD5')))
            raise AuthenticationError()
    date_header = request.get_header('Date')
    if date_header is None:
        raise AuthenticationError()
    try:
        date = datetime(*parsedate(date_header)[:6])
    except (ValueError, TypeError):
        log.debug('SIGNED REQUEST: wrong date format')
        raise AuthenticationError()
    delta = datetime.utcnow() - date
    if delta < timedelta(0) or delta > timedelta(0, 300):
        log.info('SIGNED REQUEST: date delta error')
        raise AuthenticationError()
    try:
        id, signature = credentials.split(':', 1)
        log.debug('SIGNED REQUEST: encoding info for %s' % id)
        return credentials
    except ValueError:
        log.exception('HTTP REST authenticator failed')
        raise AuthenticationError()

    
def build_string_to_sign(request, url=None, headers=None):
    """Return the string used to authenticate the request.

    The client must have provided a signed version of this string.

    The string is the concatenation of the http verb, url and values of the
    http request header fields specified in ``headers_to_sign``.
    """
    if headers is None:
        headers = HEADERS_TO_SIGN
    if url is None:
        url = request.url
    get_header = lambda field: request.get_header(field, '')
    return (request.http_method() + url +
            ''.join(map(get_header, headers)))


def authenticate_user(session, tokenid, signed_content, signature):
    """Authenticate a user from a AuthToken id by checkig the
    request's signature is correct. 

    :session: a cubicweb connection (usually a repo.internal_cnx()
              since it must have read access to the AuthToken)
    
    :tokenid: the AuthToken id belonging to the CWUser being authenticated

    :request: the http request

    :signature: the signature (usually extracted from the headers using get_credentals_from_headers) 

    Warning: it does not check whether the user is enabled or not.

    Returns the user's eid on success.

    """
    try:
        rset = session.execute('Any U, K WHERE T token_for_user U, '
                               '               T token K, '
                               '               T enabled True, '
                               '               T id %(id)s',
                               {'id': tokenid})
        if not rset:
            return
        assert len(rset) == 1
        user_eid, secret_key = rset[0]
        expected_signature = hmac.new(str(secret_key),
                                      signed_content).hexdigest()
        if compare_digest(expected_signature, signature):
            return user_eid
        else:
            session.info('request content signature check failed for %s (signed content is %r)', tokenid, signed_content)
    except Exception as exc:
        session.debug('authentication failure (%s)', exc)
    
