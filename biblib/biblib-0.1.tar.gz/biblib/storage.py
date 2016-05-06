# vim: set fileencoding=utf-8 :
"""
This module contains basic reader and writer classes,
with the interfaces implemented as abstract base classes.

They will handle ids (cite keys), entries and dictonaries ({'cite key': entry})
as input and will return an entry or a dictonary ({'cite key': entry}).

The following classes are provided:

- Abstract Base Classes
    - :py:class:`ReadStorage <biblib.storage.ReadStorage>`
    - :py:class:`WriteStorage <biblib.storage.WriteStorage>`
- String
    - :py:class:`StringReadStorage <biblib.storage.StringReadStorage>`
    - :py:class:`StringStorage <biblib.storage.StringStorage>`
- File
    - :py:class:`FileReadStorage <biblib.storage.FileReadStorage>`
    - :py:class:`FileStorage <biblib.storage.FileStorage>`
- DOI
    - :py:class:`DoiReadStorage <biblib.storage.DoiReadStorage>`
- ISBN
    - :py:class:`IsbnReadStorage <biblib.storage.IsbnReadStorage>`
- SQLite
    - :py:class:`SqliteStorage <biblib.storage.SqliteStorage>`


>>> from biblib.storage import FileStorage, DoiReadStorage
>>> # init storages
>>> doiStorage = DoiReadStorage()
>>> storage = FileStorage('/path/to/file.bib')
>>> # read entries from file
>>> entries = storage.readEntries()
{'CiteKey': <biblib._entry.Entry object at 0x808184390>}
>>> # fetch entry from doi and add it to the file storage
>>> entry = doiStorage.readEntry('10.1103/physrevlett.108.105901')
>>> storage.createEntry(entry, 'OtherCiteKey')
>>> entries = storage.readEntries()
{'CiteKey': <biblib._entry.Entry object at 0x808184390>, 'OtherCiteKey': <biblib._entry.Entry object at 0x8081eef90>}

"""

from ._entry import Entry
from .dev._parser import parse_data
from .dev._parser import record_to_bibtex
from .dev._doilib import doi2bibtex
from .dev._isbnlib import isbn2bibtex
from .dev._doilib import DOIError
import magic
from collections import OrderedDict

import sqlite3

from abc import ABCMeta, abstractmethod


class ReadStorage(object):
    """
    AbstractBaseClass ReadStorage

    :param str src: data source to act on
    """

    __metaclass__ = ABCMeta

    def __init__(self, src):
        self._src = src

    @abstractmethod
    def readEntry(self, id):
        """
        Return Entry for given id.
        (abstract method, must be implemented in derived classes)

        :param str id: ID of Entry
        :return: Entry object for the given id
        :rtype: :class:`Entry <biblib.Entry>` or None
        """
        return None

    @abstractmethod
    def readEntries(self, ids=None):
        """
        Return list of Entries for given ids.
        Returns all stored Entries if list ist empty.

        :param list ids: IDs of Entries
        :return: Entry objects for given ids
        :rtype: dict of :class:`Entries <.Entry>`
        """
        return {}


class WriteStorage(object):
    """
    AbstractBaseClass WriteStorage

    :param str src: data source to act on
    """

    __metaclass__ = ABCMeta

    def __init__(self, src):
        self._src = src

    @abstractmethod
    def createEntry(self, entry, id=None):
        """
        Add Entry to storage source

        :param entry: Entry to store
        :type entry: :class:`.Entry`
        :param str id: id to store entry with
        """
        pass

    @abstractmethod
    def updateEntry(self, entry, id=None):
        """
        update Entry in storage source

        :param entry: Entry to store
        :type entry: :class:`.Entry`
        :param str id: id to store entry with
        """
        pass

    @abstractmethod
    def deleteEntry(self, entry, id=None):
        """
        delete Entry from storage source

        :param entry: Entry to store
        :type entry: :class:`.Entry`
        :param id: id to store entry with
        :type id: str or None
        """
        pass

    @abstractmethod
    def writeEntries(self, entries=None):
        """
        Overwrite storage with given Entries.
        Existing entries will be purged.

        :param entries: list of Entry objects
        :type entries: list of Entries
        """
        pass

    def _getCiteKey(self, entry, citeKey=None):
        """Helper to identify the citeKey"""
        if citeKey:
            return citeKey
        return entry.ckey


################################################################################
#
# IMPLEMENTATIONS
#
################################################################################


class StringReadStorage(ReadStorage):
    """
    ReadStorage that stores the data in a string.

    :param bibStr: BibTex string
    :type bibStr: str
    """

    @classmethod
    def entriesFromString(self, bibStr):
        """
        Transform bibtex string into a dictonary of Entries.

        :param bibStr: bibtex string
        :type bibStr: unicode
        :return: dictonary of Entries
        :rtype: dict of Entries
        """
        entries = OrderedDict()
        # parses a bibStr
        entryDicts = parse_data(bibStr, decode=True)

        for entryDict in entryDicts:
            entry = Entry.get_Instance(entryDict)
            entries[entryDict['ID']] = entry

        return entries

    def __init__(self, bibStr):
        super(StringReadStorage, self).__init__(bibStr)

    @classmethod
    def entryFromString(self, bibStr):
        """
        Transform bibtex string into an Entry.
        If string contains more than one Entry the first one will be returned.

        :param bibStr: bibtex string
        :type bibStr: unicode
        :return: Entry
        :rtype: Entry or None
        """
        entries = StringReadStorage.entriesFromString(bibStr)
        if entries:
            return entries.popitem(False)[1]
        return None

    def _selectEntries(self, entries, citeKeys=None):
        """
        Return list of Entries for given citeKeys.
        Returns all Entries if list of citeKeys is empty.

        :param entries: dictonary of Entries to do lookup for.
        :type: dict of Entries
        :param citeKeys: citeKeys of Entries
        :type citeKeys: list of strings
        :return: Entry objects
        :rtype: dict of Entries
        """
        if citeKeys:
            result = {}
            for citeKey in citeKeys:
                if citeKey in entries:
                    result[citeKey] = entries[citeKey]

            return result

        return entries

    def readEntry(self, citeKey):
        result = self.readEntries([citeKey])
        if result:
            return result[citeKey]
        return None

    def readEntries(self, citeKeys=None):
        entries = StringReadStorage.entriesFromString(self._src)
        return self._selectEntries(entries, citeKeys)

    def str(self):
        return self._src

    def __str__(self):
        return self.str()


class StringStorage(StringReadStorage, WriteStorage):
    """
    ReadWriteStorage that stores the data in a string.

    :param str bibStr: BibTex string
    :param str encoding: string encoding
    """

    def __init__(self, src, encoding='ascii'):
        super(StringStorage, self).__init__(src)
        self.encoding = encoding

    @classmethod
    def entriesToString(self, entries, encoding='ascii'):
        bibStr = ''
        for citeKey, entry in entries.items():
            bibStr += StringStorage.entryToString(entry, citeKey, encoding=encoding)
        return bibStr

    @classmethod
    def entryToString(self, entry, citeKey=None, encoding='ascii'):
        """
        Returns the BibTeX code of an Entry objects as a string.
        If *citeKey* is not defined, the object attribute :attr:`.Entry.citeKey` will be used.

        :param entryObj: BibTeX Entry
        :type entryObj: :class:`.Article` | :class:`.Book` | ...
        :param str citeKey: citation-key
        :param str encoding: string encoding
        :return: BibTeX string
        :rtype: str
        """

        data = entry.datadict
        return record_to_bibtex(data, citeKey, encoding)

    def createEntry(self, entry, citeKey=None):

        entries = self.readEntries()
        citeKey = self._getCiteKey(entry, citeKey)

        entries[citeKey] = entry
        self.writeEntries(entries)

    def updateEntry(self, entry, citeKey=None):

        entries = self.readEntries()
        citeKey = self._getCiteKey(entry, citeKey)

        if citeKey in entries:
            entries[citeKey] = entry
        self.writeEntries(entries)

    def deleteEntry(self, entry, citeKey=None):

        entries = self.readEntries()
        citeKey = self._getCiteKey(entry, citeKey)

        if citeKey in entries:
            del entries[citeKey]
        self.writeEntries(entries)

    def writeEntries(self, entries=None):
        """
        Overwrite storage with given Entries.
        Existing entries will be purged.

        :param entries: list of Entry objects
        :type entries: list of Entries
        """
        entries = entries or {}
        self._src = StringStorage.entriesToString(entries, self.encoding)


class FileReadStorage(StringReadStorage):
    """
    ReadStorage that reads the data from a file.

    :param str file: path to file
    """

    def __init__(self, file):
        super(FileReadStorage, self).__init__(file)
        with open(file, 'a'):
            pass

    def readEntries(self, citeKeys=None):
        bibStr = self._readFile()
        entries = StringReadStorage.entriesFromString(bibStr)
        return self._selectEntries(entries, citeKeys)

    def _readFile(self):
        """Helper method"""
        m = magic.Magic(mime_encoding=True)
        encoding = m.from_file(self._src)
        # read the file to a string
        try:
            with open(self._src, 'r') as f:
                return f.read().decode(encoding)
        except LookupError:
            with open(self._src, 'r') as f:
                return f.read().decode('utf8')
        except (AttributeError, UnicodeDecodeError):
            try:
                with open(self._src, 'r') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(self._src, 'r', encoding='utf8') as f:
                    return f.read()


class FileStorage(FileReadStorage, StringStorage):
    """
    ReadWriteStorage that stores the data in a file.

    :param str file: path to file
    :param str encoding: string encoding
    """

    def __init__(self, file, encoding='ascii'):
        super(FileStorage, self).__init__(file)
        self.encoding = encoding

    def writeEntries(self, entries):
        header = '% Encoding: {encoding}'.format(encoding=self.encoding.upper()+"\n\n")

        bibStr = StringStorage.entriesToString(entries, self.encoding)

        with open(self._src, 'w') as f:
            f.write(header)
            f.write(bibStr)


class DoiReadStorage(ReadStorage):
    """
    ReadStorage that reads the data from the doi database.
    """

    def __init__(self):
        pass

    def readEntry(self, doi):
        try:
            return StringReadStorage.entryFromString(doi2bibtex(doi))
        except DOIError:
            return None

    def readEntries(self, dois=None):
        dois = dois or []
        entries = {}
        for doi in dois:
            entries[doi] = self.readEntry(doi)
        return entries


class IsbnReadStorage(ReadStorage):
    """
    ReadStorage that reads the data for a given ISBN.
    """

    def __init__(self):
        pass

    def readEntry(self, isbn):
        bibStr = isbn2bibtex(isbn)
        if bibStr:
            return StringReadStorage.entryFromString(bibStr)
        else:
            return None

    def readEntries(self, isbns=None):
        isbns = isbns or []
        entries = {}
        for isbn in isbns:
            entries[isbn] = self.readEntry(isbn)
        return entries


class SqliteStorage(ReadStorage, WriteStorage):
    """
    ReadWriteStorage that stores the data in SQLite3 database

    :param file: path to db file
    :type file: str
    """

    _tableName = "biblib_entries"

    def __init__(self, src):
        super(SqliteStorage, self).__init__(src)
        self._connection = sqlite3.connect(self._src)
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()
        self._initDb()

    def __del__(self):
        self._connection.close()

    def _initDb(self):

        cols = []
        for colName in ['ID', 'ENTRYTYPE'] + Entry.processedTags + Entry.protectedTags:
            cols.append(colName + " TEXT")

        initTable = " CREATE TABLE IF NOT EXISTS " + self._tableName
        initTable += " (" + ", ".join(set(cols)) + ")"
        self._cursor.execute(initTable)
        self._connection.commit()

    def _queryEntries(self, query, params=None):
        params = params or tuple()
        result = {}
        for row in self._cursor.execute(query, params):
            result[row['ID']] = Entry.get_Instance({k: v for k, v in dict(row).items() if v is not None})
        return result

    def readEntry(self, id):
        for entry in self._queryEntries("SELECT * from %s WHERE ID=?" % self._tableName, (id,)).values():
            return entry
        return None

    def readEntries(self, ids=None):
        if ids:
            return self._queryEntries("SELECT * from %s WHERE ID in (%s)" % (self._tableName, ('?,' * len(ids))[0:-1]), tuple(ids))
        else:
            return self._queryEntries("SELECT * from " + self._tableName)

    def createEntry(self, entry, citeKey=None):
        data = dict(entry.datadict)
        data['ID'] = self._getCiteKey(entry, citeKey)
        insert = "INSERT INTO %s (%s) VALUES (%s)" % (self._tableName, ','.join(data.keys()), str(('?,' * len(data))[0:-1]))
        with self._connection:
            self._connection.execute(insert, tuple(data.values()))

    def updateEntry(self, entry, citeKey=None):
        data = dict(entry)
        data['ID'] = self._getCiteKey(entry, citeKey)

        fields = [k + "==:" + k for k in data]
        update = "UPDATE " + self._tableName + " SET " + ", ".join(fields) + " WHERE ID==:ID"
        with self._connection:
            self._connection.execute(update, data)

    def deleteEntry(self, entry, citeKey=None):
        id = self._getCiteKey(entry, citeKey)
        with self._connection:
            self._connection.execute("DELETE FROM %s WHERE ID=?" % self._tableName, (id,))

    def writeEntries(self, entries=None):
        entries = entries or {}
        with self._connection:
            self._connection.execute('DROP TABLE IF EXISTS ' + self._tableName)
            self._initDb()
        for citeKey, entry in entries.items():
            self.createEntry(entry, citeKey)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
