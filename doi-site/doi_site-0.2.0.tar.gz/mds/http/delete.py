'''
This module is used to make HTTP DELETE calls.
'''

import base64
import logging
import socket
from ssl import SSLError
import urllib2
from urlparse import urljoin

from django.http import HttpResponse

from doi_site.settings import DATACITE_URL, DOI_PREFIX, DATACITE_USER_NAME, \
    DATACITE_PASSWORD, TIME_OUT
from mds.http.helper import get_doi_from_request, get_opener, get_response, \
    is_authorized


LOGGING = logging.getLogger(__name__)


def delete_metadata(request):
    """
    Delete the metadata for the DOI.

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a HTTPResponse

    """
    _doi = get_doi_from_request(request, 'metadata')
    LOGGING.info('Delete metadata doi: %s', _doi)
    url = urljoin(DATACITE_URL, request.get_full_path())
    try:
        doi_suffix = _doi.split(DOI_PREFIX, 1)[1]
    except IndexError:
        return get_response("Bad Request - wrong prefix, doi should start " \
                            "with %s" % DOI_PREFIX, 400)

    if not is_authorized(request, doi_suffix):
        return get_response("Unauthorized - insufficient privileges", 403)
    return _delete(url)


def _delete(url):
    """
    Send a delete request to DataCite.

    Args:
        url (str): The URL to call

    Return:
        a HTTPResponse

    """
    _set_timeout()
    opener = get_opener()
    auth_string = (base64.encodestring(DATACITE_USER_NAME + ':'
                                       + DATACITE_PASSWORD)).rstrip()
    headers = {'Authorization':'Basic ' + auth_string}
    req = urllib2.Request(url, data=None, headers=headers)
    req.get_method = lambda: 'DELETE'
    try:
        response = opener.open(req)
    except (urllib2.HTTPError) as ex:
        msg = ex.readlines()
        LOGGING.warn('HTTPError error getting %s. %s', url, msg)
        return get_response(msg, ex.code)
    except (socket.timeout, urllib2.URLError) as ex:
        LOGGING.warn('Timeout or URLError error getting %s. %s', url, ex.reason)
        return get_response(ex.reason, 500)
    except (SSLError) as ex:
        LOGGING.warn('SSLError error getting %s. %s', url, ex)
        return get_response(ex, 500)
    finally:
        _close(opener)
    if response.headers.has_key('Content-Type'):
        ret_response = HttpResponse(content_type=
                                    response.headers.get('Content-Type'))
    else:
        ret_response = HttpResponse()
    ret_response.status_code = response.code
    ret_response.reason_phrase = response.msg
    # pylint: disable=maybe-no-member
    ret_response.writelines(response.readlines())
    return ret_response


def _set_timeout():
    """
    Set the time out used by urllib.

    """
    socket.setdefaulttimeout(TIME_OUT)


def _close(opener):
    """
    Close the URL opener.

    """
    try:
        opener.close()
    # pylint: disable=bare-except
    except:
        pass
