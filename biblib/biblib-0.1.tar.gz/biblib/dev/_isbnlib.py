# -*- coding: utf-8 -*-
"""
This module contains functions related to the International Standard Book Number (ISBN).

"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__ = filter(str.isdigit, "$Revision: 92 $")


# import external modules
import isbnlib

# import of internal package modules
from ._parser import record_to_bibtex


def isbn2bibtex(isbn):
    """
    Returns the BibTeX citation Entry for a publication with a given ISBN.

    :param isbn: International Standard Book Number (ISBN)
    :type isbn: str
    :return: the *formatted* BibTeX Entry of the publication
    :rtype: str
    """
    inputdict = _isbn_to_inputdict(isbn)
    if inputdict:
        return record_to_bibtex(inputdict)
    else:
        return None


def _isbn_to_inputdict(isbn):
    """
    If meta data is available for the given ISBN, it returns a valid inputdict for an entry object,
    else it returns *None*.

    :param isbn: International Standard Book Number (ISBN)
    :type isbn: str
    :return: inputdict
    :rtype: dict
    """
    meta_data = _metaData_from_ISBN(isbn)
    if meta_data:
        return _meta_to_inputdict(meta_data)
    else:
        return None


def _meta_to_inputdict(metaDict):
    """
    Converts a dictionary as returned by the isbnlib.meta() function to
    a valid inputdict for an entry object.

    :param metaDict: meta data
    :type metaDict: dict
    :return: inputdict
    :rtype: dict
    """
    inputDict = {}
    for key, vakue in metaDict.items():
        new_key = key.lower()
        # key name correction
        if new_key == 'authors':
            new_key = 'author'
        if new_key == 'isbn-13':
            new_key = 'isbn'
        inputDict[new_key] = metaDict[key]
    # set citation-key
    inputDict['ID'] = str(inputDict.get('isbn', 'unknown'))
    # set type to 'Book'
    inputDict['ENTRYTYPE'] = 'book'
    # join author list
    inputDict['author'] = ' and '.join(inputDict['author'])
    return inputDict


def _metaData_from_ISBN(isbn):
    """
    Returns the meta data for a given ISBN number.
    If the ISBN number is invalid or no meta data is available, it returns *None*.

    :param isbn: ISBN number
    :type isbn: str
    :return: meta data
    :rtype: dict
    """
    try:
        metaDict = isbnlib.meta(isbn=isbn)
    except isbnlib._exceptions.NotValidISBNError as e:
        metaDict = None
    return metaDict
