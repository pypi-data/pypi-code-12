# -*- coding: utf-8 -*-
"""
This package contains object classes and functions to manage BibTeX entries and databases within Python.

Terms are used here according to http://www.bibtex.org.

"""
__license__ = "MIT"
__docformat__ = 'reStructuredText'
__version__ = '0.1'
__revision__ = filter(str.isdigit, "$Revision: 216 $")

# main modules
from ._entry import (Entry, Techreport, Phdthesis, Misc, Inproceedings, Incollection, Unpublished,
                     Manual, Mastersthesis, Proceedings, Book, Booklet, Inbook, Article)
from ._bibdb import BibDB, StorageBibDB, StringBibDB, FileBibDB, SqliteBibDB, DoiBibDB, IsbnBibDB, BibDBCollection
from ._btfile import (BibTexFile, BibTexFileSet)

__all__ = ['Entry', 'Techreport', 'Phdthesis', 'Misc', 'Inproceedings', 'Incollection', 'Unpublished',
        'Manual', 'Mastersthesis', 'Proceedings', 'Book', 'Booklet', 'Inbook', 'Article',
        'BibDB', 'StorageBibDB', 'StringBibDB', 'FileBibDB', 'DoiBibDB', 'IsbnBibDB', 'SqliteBibDB',
        'db_from_string', 'db_from_file', 'db_from_doiList', 'db_from_isbnList',
        'entry_from_doi', 'entry_from_isbn',
        'db_to_string', 'db_to_file', 'entry_to_string',
        'BibTexFile', 'BibTexFileSet',
        'BibDBCollection',
        ]

def entry_from_doi(doi):
    """
    Creates an entry object by DOI.

    :param str doi: DOI ss string
    :return: BibTeX entry object
    :rtype: :class:`.Article` | :class:`.Book` | ...
    """
    return DoiBibDB()[doi]

def entry_from_isbn(isbn):
    """
    Creates an entry object by ISBN.

    :param str isbn: ISBN ss string
    :return: BibTeX entry object
    :rtype: .Book
    """
    return IsbnBibDB()[isbn]

def db_from_string(bibStr, method=None):
    """
    Function parsing a BibTeX bibStr containing one or more entries
    and returns a BibTeX database object.

    :param unicode bibStr: input BibTeX string
    :param str method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :return: BibTeX database object
    :rtype: .BibDB
    """
    srcDb = StringBibDB(bibStr)
    db = BibDB()
    db.merge_bibdb(srcDb, method)
    return db

def db_from_file(filename, method=None):
    """
    Function parsing a BibTeX file containing one or more entries
    and returns a BibTeX database object.

    :param str filename: input BibTeX file
    :param str method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :return: BibTeX database object
    :rtype: .BibDB
    """
    srcDb = FileBibDB(filename)
    db = BibDB()
    db.merge_bibdb(srcDb, method=None)
    return db

from .storage import DoiReadStorage
def db_from_doiList(doiList, method=None):
    """
    Function to retrieve BibTeX citation entries by their DOI
    and returns a BibTeX database object.

    :param list doiList: list of DOIs as strings
    :param str method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :return: BibTeX database object
    :rtype: .BibDB
    """
    storage = DoiReadStorage()
    entries = storage.readEntries(doiList).values()
    return BibDB(entries, method)

from .storage import IsbnReadStorage
def db_from_isbnList(isbnList, method=None):
    """
    Function to retrieve BibTeX citation entries by their ISBN
    and returns a BibTeX database object.

    :param list isbnList: list of ISBN numbers as strings
    :param str method: keyword for merging method (see :meth:`.BibDB.add_entry`)
    :return: BibTeX database object
    :rtype: .BibDB
    """
    storage = IsbnReadStorage()
    entries = storage.readEntries(isbnList).values()
    return BibDB(entries, method)

def db_to_string(db, encoding='ascii'):
    """
    Returns the BibTeX code of a database objects as a string.

    :param db: BibTeX database
    :type db: .BibDB
    :param str encoding: string encoding
    :return: BibTeX code
    :rtype: str
    :raises TypeError: if *db* is not a valid database object
    """
    strDB = StringBibDB('', encoding=encoding)
    strDB.merge_bibdb(db)
    return str(strDB)

def db_to_file(db, filename, encoding='ascii'):
    """
    Writes a database objects to a BibTeX *file*.

    :param db: BibTeX database
    :type db: .BibDB
    :param str filename: output file name
    :param str encoding: string encoding
    :raises TypeError: if *db* is not a valid database object
    """

    FileBibDB(filename, encoding).merge_bibdb(db)

def entry_to_string(entry, ckey=None, encoding='ascii'):
    """
    Returns the BibTeX code of an Entry objects as a string.
    If *ckey* is not defined, the object attribute :attr:`.Entry.ckey` will be used.

    :param entryObj: BibTeX Entry
    :type entryObj: :class:`.Article` | :class:`.Book` | ...
    :param ckey: citation-key
    :type ckey: str
    :param str encoding: string encoding
    :return: BibTeX code
    :rtype: str
    :raises TypeError: if *entryObj* is not a valid Entry object
    """
    db = StringBibDB('', encoding=encoding)
    db.add_entry(entry, ckey)
    return str(db)

