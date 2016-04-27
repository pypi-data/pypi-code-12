'''
This module is used to make HTTP POST calls.
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
import xml.etree.ElementTree as ET


LOGGING = logging.getLogger(__name__)


def post_doi(request):
    """
    Post the DOI.

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a HTTPResponse

    """
    LOGGING.info('Post doi')
    try:
        _doi = _get_doi_from_text_body(request.body)
    except IndexError:
        return get_response("Bad Request - request body must be exactly two " \
                            "lines: DOI and URL", 400)
    LOGGING.debug('Post doi, doi: %s', _doi)

    try:
        doi_suffix = _doi.split(DOI_PREFIX, 1)[1]
    except IndexError:
        return get_response("Bad Request - wrong prefix, doi should start " \
                            "with %s" % DOI_PREFIX, 400)

    if not is_authorized(request, doi_suffix):
        return get_response("Unauthorized - insufficient privileges", 403)

    url = urljoin(DATACITE_URL, request.get_full_path())
    return _post(url, request.body, _get_content_type_header(request))


def post_media(request):
    """
    Post the media.

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a HTTPResponse

    """
    LOGGING.info('Post media')
    _doi = get_doi_from_request(request, 'media')
    if _doi == None:
        return get_response("Bad Request - doi not found in URL", 400)
    LOGGING.debug('Post media, doi: %s', _doi)
    try:
        doi_suffix = _doi.split(DOI_PREFIX, 1)[1]
    except IndexError:
        return get_response("Bad Request - wrong prefix, doi should start " \
                            "with %s" % DOI_PREFIX, 400)

    if not is_authorized(request, doi_suffix):
        return get_response("Unauthorized - insufficient privileges", 403)

    url = urljoin(DATACITE_URL, request.get_full_path())
    return _post(url, request.body, _get_content_type_header(request))


def post_metadata(request):
    """
    Post the metadata.

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a HTTPResponse

    """
    LOGGING.info('Post metadata')
    try:
        _doi = _get_doi_from_xml_body(request.body)
    except ET.ParseError as ex:
        LOGGING.info('Error parsing xml from users request: %s', ex)
        return get_response("Bad Request - error parsing xml: %s" % ex, 400)
    if _doi == None:
        return get_response("Bad Request - doi not found in XML", 400)
    LOGGING.debug('Post metadata, doi: %s', _doi)
    try:
        doi_suffix = _doi.split(DOI_PREFIX, 1)[1]
    except IndexError:
        return get_response("Bad Request - wrong prefix, doi should start " \
                            "with %s" % DOI_PREFIX, 400)

    if not is_authorized(request, doi_suffix):
        return get_response("Unauthorized - insufficient privileges", 403)

    url = urljoin(DATACITE_URL, request.get_full_path())
    return _post(url, request.body, _get_content_type_header(request))


def _post(url, body, headers):
    """
    Send a post request to DataCite.

    Args:
        url (str): The URL to call
        body (str): The data
        headers (dict): A dictionary of headers to use

    Return:
        a HTTPResponse

    """
    _set_timeout()
    opener = get_opener()
    auth_string = (base64.encodestring(DATACITE_USER_NAME + ':'
                                       + DATACITE_PASSWORD)).rstrip()
    headers.update({'Authorization':'Basic ' + auth_string})

    # If the request body is a string, urllib2 attempts to concatenate the url,
    # body and headers. If the url is unicode, the request body can get
    # converted unicode. This has resulted in issues where there are characters
    # with diacritic marks in the request body. To avoid these issues the url is
    # UTF-8 encoded.
    url_encode = url.encode('utf-8')

    req = urllib2.Request(url_encode, data=body, headers=headers)
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
    except UnicodeDecodeError as ex:
        LOGGING.info('UnicodeDecodeError error getting %s. %s', url, ex)
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
    if response.headers.has_key('location'):
        ret_response.setdefault('Location', response.headers.get('location'))
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


def _get_doi_from_text_body(body):
    """
    Get the DOI from the body of a request.

    Args:
        body (str): The data

    Return:
        a str containing the DOI

    """
    bits = body.split('url=', 1)
    if bits[0] != '':
        _doi = (bits[0].split('doi=')[1]).strip()
    else:
        bits = bits[1].split('doi=')
        _doi = bits[1].strip()

    return _doi


def _get_doi_from_xml_body(body):
    """
    Get the DOI from the body of a request where the DOI is embedded in the
    metadata XML.

    Args:
        body (str): The data

    Return:
        a str containing the DOI

    Throws:
        ParseError

    """
    root = ET.fromstring(body)
    for child in root.getchildren():
        if child.attrib == {'identifierType': 'DOI'}:
            return child.text
    return None


def _get_content_type_header(request):
    """
    Get the content type from the request. Return an empty dict if it is not set

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a dict containing the content type

    """
    try:
        return {'Content-Type':request.META['CONTENT_TYPE']}
    except KeyError:
        return {}
