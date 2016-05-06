# -*- coding: utf-8 -*-
"""
This module contains functions related to the digital object identifier (DOI).

"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__ = filter(str.isdigit, "$Revision: 172 $")


# import external modules
import magic
import sys
if sys.version_info < (3,):
    from urllib2 import urlopen, Request, HTTPError
else:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

# import of internal package modules
from ._parser import parse_data


def doi2bibtex(doi):
    """
    Returns the BibTeX citation Entry for a publication with a given DOI,
    by using the web service of https://www.doi.org.

    .. seealso:: http://crosscite.org/cn/

    :param doi: DOI of the publication
    :type doi: str
    :return: the *formatted* BibTeX Entry of the publication
    :rtype: str
    :raises biblib.dev.DOIError: if DOI didn't exist or no contents is available
    :raises urllib2.URLError: if a connection error occurs
    """

    url = 'http://dx.doi.org/%s' % doi
    headers = {'Accept': 'application/x-bibtex; charset=utf-8'}
    request = Request(url, headers=headers)

    try:
        resp = urlopen(request)

    except HTTPError as e:
        raise DOIError(e.code)

    bibtexentry = resp.read()

    # determine the encoding of the file
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(bibtexentry).decode()

    return bibtexentry.decode(encoding)


def _doi_to_inputdict(doi, decode=True):
    """
    If meta data is available for the given DOI, it returns a valid inputdict for an entry object,
    else it returns *None*.

    :param doi: DOI
    :type doi: str
    :param decode: LaTeX codes to unicode character
    :type decode: bool
    :return: inputdict
    :rtype: dict
    """
    # get bibtex string from DOI
    bibstr = doi2bibtex(doi)

    # parses a bibStr
    listOfDicts = parse_data(bibstr, decode)

    if listOfDicts:
        return listOfDicts[0]
    else:
        return None


class DOIError(Exception):
    """
    Exception raised for errors with the request of a BibTeX citation Entry
    at http://dx.doi.org by the DOI.

    Beside the conventional meaning of HTTP response status codes, the
    following codes are redefined:

    * 204: The request was OK but there was no metadata available.
    * 404: The DOI requested doesn't exist.
    * 406: Can't serve requested content type.

    :param code: HTTPError code send by dx.doi.org
    :type code: int
    """

    def __init__(self, code):
        self.code = code
        if code == 204:
            msg = 'The request was OK but there was no metadata available.'
        elif code == 404:
            msg = "The DOI requested doesn't exist."
        elif code == 406:
            msg = "Can't serve requested content type."
        else:
            msg = 'HTTPError ' + str(code)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
