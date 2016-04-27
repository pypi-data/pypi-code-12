'''
Helper methods/ common functionality.
'''

import urllib2

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from doi_site import settings


def is_authorized(request, doi_suffix):
    """
    Check if the user is authorised to use the suffix.

    Args:
        request (HTTPRequest): The HTTP request
        doi_suffix (str): The DOI suffix

    Return:
        a boolean, True if the user is authorised

    """
    # decode precent encoding and remove leading '/' before checking doi
    doi_suffix = urllib2.unquote(doi_suffix)
    if doi_suffix.startswith('/'):
        doi_suffix = doi_suffix.split('/', 1)[1]
    authorized_dois = []
    groups = request.user.groups.iterator()
    for group in groups:
        try:
            authorized_dois.append(group.groupprofile.doi_suffix)
        except ObjectDoesNotExist:
            pass
    for auth_doi in authorized_dois:
        if doi_suffix.startswith(auth_doi):
            return True

    return False


def get_accept_header(request):
    """
    Extract the accept header from the request.

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a dict, if present key = 'Accept'

    """
    try:
        return {'Accept':request.META['HTTP_ACCEPT']}
    except KeyError:
        return {}


def get_doi_from_request(request, method):
    """
    Extract the doi from the request.

    Args:
        request (HTTPRequest): The HTTP request

    Return:
        a str, the DOI

    """
    full_path = request.get_full_path()
    bits = full_path.split(method + '/')
    try:
        return bits[1]
    except IndexError:
        return None


def get_response(message, code):
    """
    Create a response.

    Args:
        message (str): The message to include in the response
        code (str): The return code to include in the response

    Return:
        a dict, if present key = 'Accept'

    """
    response = HttpResponse(status=code)
    # pylint: disable=no-member
    response.writelines(message)
    return response


def get_opener():
    """
    Get a http opener.
    A check is made to see if a proxy should be used.
    
    Return:
        an opener object

    """
    if _is_use_proxy():
        proxy_handler = urllib2.ProxyHandler({'https': getattr(settings, 
            'HTTP_PROXY_HOST') + ":" + getattr(settings, 'HTTP_PROXY_PORT')})
        return urllib2.build_opener(proxy_handler)
    else:
        return urllib2.build_opener()


def _is_use_proxy():
    """
    Test to see if we should be using a http proxy.

    Return:
        boolean, True to use proxy

    """
    if (getattr(settings, 'HTTP_PROXY_HOST', False) and
        getattr(settings, 'HTTP_PROXY_PORT', False)):
        return True
    return False
