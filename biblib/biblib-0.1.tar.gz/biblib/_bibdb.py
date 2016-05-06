# -*- coding: utf-8 -*-
"""
ThisThis module contains the BibTeX database class.

"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__ = filter(str.isdigit, "$Revision: 218 $")


import string
import sys
from unidecode import unidecode

# import of internal package modules
from . import _entry
from . import storage as bibstorage

if sys.version_info < (3,):
    range = xrange
else:
    unicode = str


class BibDB(object):
    """
    This is the BibTeX database main class.

    Optional a database can be initially populate by a list of Entry objects.

    :param ListOfEntryObj: list of BibTeX Entry object (:class:`.Article` | :class:`.Book` | ...)
    :type ListOfEntryObj: .BibDB.data
    :param method: keyword for merging method (see :meth:`.add_entry`)
    :type method: str
    :return: BibTeX database object
    :rtype: .BibDB
    :raises TypeError: if an *EntryObj* is not of a valid object type
    :raises KeyError: if there is trouble with a citation-key of an *EntryObj*
    """

    # generate lists for counters used in proposeCKey()
    _clist = {
        'alpha': string.ascii_lowercase,
        'Alpha': string.ascii_uppercase,
        'num': range(0, sys.maxsize)
    }

    def __init__(self, ListOfEntryObj=None, method=None):

        #: Template for a citation-key, based on the tag names within an Entry.
        #: By default: ``{family}{year}``, here *family* refers to the first author family name.
        self.ckey_tpl = '{family}{year}'

        #: Template for a citation-key with a counter.
        #: By default: ``{family}{year}{cnt}``, here *cnt* will be replaced with the choosen counter (:attr:`.ckey_tpl_cnt`).
        self.ckey_tpl_wc = '{family}{year}{cnt}'

        #: Counter style for the citation-key template: ``alpha`` (*default* a,b,..,z), ``Alpha`` (A,B,..,Z) or ``num`` (1,2,3,...).
        self.ckey_tpl_cnt = 'alpha'

        # initiate variables
        self._data = {}

        # initially populate database
        if ListOfEntryObj:
            for EntryObj in ListOfEntryObj:
                self.add_entry(EntryObj, method=method)

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        """
        Returns a list of citation-keys defined in the database.

        :return: list of citation-keys
        :rtype: list
        """
        return self._data.keys()

    def values(self):
        """
        Returns a list of entry objects stored in the database.

        :return: list of entry objects
        :rtype: list
        """
        return self._data.values()

    def items(self):
        """
        Returns a list of sets containing citation-key/entry object.

        :return: list of sets citation-key/entry object
        :rtype: list
        """
        return self._data.items()

    def get_entry(self, ckey):
        """
        Returns the Entry object with the given citation-key in the database.

        :param ckey: citation-key
        :type ckey: str
        :return: BibTeX Entry object
        :rtype: :class:`.Article` | :class:`.Book` | ...
        :raises KeyError: if citation-key did not exist in database
        """
        return self[ckey]

    def __getitem__(self, key):
        """
        Returns the Entry object with the given citation-key in the database.

        :param key: citation-key
        :type key: str
        :return: BibTeX Entry object
        :rtype: :class:`.Article` | :class:`.Book` | ...
        :raises KeyError: if citation-key did not exist in database
        """
        try:
            return self._data[key]
        except KeyError:
            msg = 'Citation-key "' + key + '" did not exists in database!'
            raise KeyError(msg)

    def add_entry(self, entryObj, ckey=None, method=None):
        """
        Adds an Entry object to the database using *ckey* or :attr:`.Entry.ckey` of *entryObj* as
        citation-key. The method argument will overwrite an existing object attribute.
        There are different methods available how to handle the citation-key.
        If *method* is:

        * ``None``: (default) an invalid or conflicting citation-key will raise a KeyError.
        * ``'lazy'``: Try to use :attr:`.Entry.ckey` of *entryObj* or *ckey* as citation-key. If the it is already in use or invalid, generate a new using :py:meth:`.proposeCKey`.
        * ``'auto'``: Always use :py:meth:`.proposeCKey` to generate a proper citation-key.
        * ``'force'``: Use :attr:`.Entry.ckey` of *entryObj* or *ckey*  as citation-key. If the it is already in used, the old Entry object will be replaced. If it is invalid, generate a new using :py:meth:`.proposeCKey`.

        :param entryObj: BibTeX Entry object
        :type entryObj: :class:`.Article` | :class:`.Book` | ...
        :param ckey: citation-key
        :type ckey: str
        :param method: keyword for adding method (see above)
        :type method: str
        :return: citation-key as used for the database
        :rtype: str
        :raises TypeError: if entryObj is not of a valid object type
        :raises KeyError: if there is trouble with a citation-key
        :raises NameError: if argument for *method* is invalid
        """
        # check if it is a valid object type
        if not isinstance(entryObj, _entry.Entry):
            msg = 'entryObj is of wrong type!'
            raise TypeError(msg)

        if not ckey:
            ckey = entryObj.ckey

        if not method:
            if not ckey or ckey in self._data:
                msg = 'Citation-key already exists in database or is invalid!'
                raise KeyError(msg)
            else:
                self._data[ckey] = entryObj
                return ckey

        elif method == 'lazy':
            if not ckey or ckey in self._data:
                ckey = self.proposeCKey(entryObj)
            self._data[ckey] = entryObj
            return ckey

        elif method == 'auto':
            ckey = self.proposeCKey(entryObj)
            self._data[ckey] = entryObj
            return ckey

        elif method == 'force':
            if not ckey:
                ckey = self.proposeCKey(entryObj)
                self._data[ckey] = entryObj
            else:
                self._data[ckey] = entryObj
                return ckey

        else:
            msg = 'Invalid value for "method" argument!'
            raise NameError(msg)

    def __setitem__(self, key, value):
        self.add_entry(value, key)

    def del_entry(self, ckey):
        """
        Deletes the Entry object with a given BibTeX citation-key.

        :param ckey: citation-key
        :type ckey: str
        :raises KeyError: if citation-key did not exist in database
        """
        del self[ckey]

    def __delitem__(self, key):
        """
        Deletes the Entry object with a given BibTeX citation-key.

        :param key: citation-key
        :type key: str
        :raises KeyError: if citation-key did not exist in database
        """
        try:
            del self._data[key]
        except KeyError:
            msg = 'Citation-key "' + key + '" did not exist in database!'
            raise KeyError(msg)


    def mod_entry_type(self, ckey, newtype):
        """
        Modifies the BibTeX Entry type for a given citation-key.

        :param ckey: citation-key
        :type ckey: str
        :param newtype: new Entry type
        :type newtype: str
        :raises KeyError: if there is trouble with a citation-key
        :raises NameError: if *newtype* is invalid
        """
        try:
            edict = self._data[ckey].datadict
            edict['ENTRYTYPE'] = newtype
            neobj = _entry.Entry.get_Instance(edict)
            self.add_entry(neobj, ckey=ckey, method='force')
        except KeyError:
            msg = 'ID "' + ckey + '" did not exist in database!'
            raise KeyError(msg)

    def update_ckey(self, old, new):
        """
        Updates the BibTeX citation-key of an Entry object in the database.

        .. note:: The citation-key stored in the respective Entry object (:attr:`.Entry.ckey`) will left unchanged!

        :param old: old citation-key
        :param new: new citation-key
        :type old: str
        :type new: str
        :raises KeyError: if one of the citation-keys are invalid
        """
        if new in self.keys():
            msg = 'New citation-key "' + new + '" alreday occupied!'
            raise KeyError(msg)

        try:
            self._data[new] = self._data.pop(old)
        except KeyError:
            msg = 'Citation-key "' + old + '" not found!'
            raise KeyError(msg)

    def proposeCKey(self, entryObj):
        """
        Proposes a BibTeX citation-key for a given Entry object.

        Based on the tag names and their contents within the Entry object and with the
        template strings (:attr:`.ckey_tpl`, :attr:`.ckey_tpl_wc`), the method will
        return a citation-key which suits the database.

        :param entryObj: BibTeX Entry object
        :type entryObj: :class:`.Article` | :class:`.Book` | ...
        :return: proposed citation-key
        :rtype: str
        :raises TypeError: if *entryObj* is not of a valid object type
        :raises KeyError: if a tag is used in :attr:`.ckey_tpl` or :attr:`.ckey_tpl_wc` which is not defined
        :raises ValueError: if :attr:`.ckey_tpl` or :attr:`.ckey_tpl_wc` string is erroneous.
        :raises IndexError: if the counter runs out of elements.
        """

        # check if it is a valid object type
        if not isinstance(entryObj, _entry.Entry):
            msg = 'entryObj is of wrong type!'
            raise TypeError(msg)

        # construct dictionary to replace keywords
        dataDict = entryObj.datadict.copy()
        if not entryObj.authors:
            dataDict.update(dict(given=u'Jon', family=u'Dow'))
        else:
            dataDict.update(entryObj.authors[0])
        dataDict['cnt'] = ''
        counterSymbols = BibDB._clist[self.ckey_tpl_cnt]

        # patch for problem:
        # UnicodeEncodeError: 'ascii' codec can't encode character ...
        for key, value in dataDict.items():
            #dataDict[key] = value.encode('us-ascii','replace')
            dataDict[key] = unidecode(unicode(value))

        # generate citation-key without counter
        ckey = self.ckey_tpl.format(**dataDict)

        # while citation-key is already in use ...
        pos = 0
        while ckey in self.keys():
            # and generat citation-key with counter
            dataDict['cnt'] = counterSymbols[pos]
            ckey = self.ckey_tpl_wc.format(**dataDict)
            pos += 1

        return ckey

    def merge_bibdb(self, dbObj, method=None):
        """
        Merges the Entry objects of another database object.
        There are different methods available how to handle the citation-key.
        It returns a dictionary where the keys refer to the original citation-key
        of an Entry object and the value to the new one used in the database.

        :param dbObj: BibTeX database object
        :type dbObj: .BibDB
        :param method: keyword for merging method (see :meth:`.add_entry`)
        :type method: str
        :return: dictionary mapping old to new citation-key
        :rtype: dict
        :raises TypeError: if dbObj is not a valid BibTeX database object
        :raises KeyError: if there is trouble with a citation-key
        :raises NameError: if argument for *method* is invalid
        """

        # check if it is a valid object type
        if not isinstance(dbObj, BibDB):
            msg = "dbObj have to be a BibTeX database object"
            raise TypeError(msg)

        # add each Entry object to the database
        out = {}
        for ckey, eObj in dbObj.items():
            out[ckey] = self.add_entry(eObj, ckey=ckey, method=method)

        return out

    def bibtex(self):
        """
        Returns the BibTeX formatted string of data base.

        .. deprecated:: 0.1.dev1-r67
            Use function :func:`.db_to_string` instead.

        :return: BibTeX formatted string
        :rtype: str
        """
        out = ''
        for ckey, entryObj in self.items():
            out += entryObj.bibtex(ckey=ckey)
        return out

    def has_ckey(self, ckey):
        """
        Test if a citation-key is defined within the database.

         .. deprecated:: 0.1.dev4
            Use ``ckey in dbOject`` instead.

        :param ckey: citation-key
        :type ckey: str
        :return: True | False
        :rtype: bool
        """
        return ckey in self._data

    def __contains__(self, key):
        return key in self._data

    def has_doi(self, doi):
        """
        Test if a DOI is defined within the database.

        :param doi: digital object identifier
        :type doi: str
        :return: True | False
        :rtype: bool
        """
        return doi in self.dois

    def __hash__(self):
        """
        Support for hash()

        :return: hash value
        """
        hashDict = {}
        for ckey, eObj in self.datadict.items():
            hashDict[ckey] = hash(eObj)
        return hash(frozenset(hashDict.items()))

    def __len__(self):
        return len(self._data)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    @property
    def datadict(self):
        """
        A dictionary containing the citation-keys as keys and the BibTeX Entry objects
        (:class:`.Article` | :class:`.Book` | ...) as values.
        """
        return self._data

    @property
    def data(self):
        """
        A list containing the BibTeX objects (:class:`.Article` | :class:`.Book` | ...) of the database.

        .. deprecated:: 0.1.dev4
            Use :meth:`.BibDB.values` instead.

        """
        return self._data.values()

    @property
    def ckeys(self):
        """
        A list of the BibTeX citation-keys of the database.

        .. deprecated:: 0.1.dev4
            Use :meth:`.BibDB.keys` instead.

        """
        return self._data.keys()

    @property
    def dois(self):
        """
        Returns a dictionary with *doi* as key and citation-key as value.
        """
        out = {}
        for ckey, eObj in self.items():
            doi = eObj.get_tag('doi')
            if doi:
                out[doi] = ckey
        return out
        #return { entryObj.get_tag('doi'): ckey for ckey, entryObj in self._data if entryObj.get_tag('doi') }


class StorageBibDB(BibDB):
    """
    StorageBibDB is a :py:class:`BibDB <biblib.BibDB>` utilizing a storage as
    defined in :py:mod:`storage <biblib.storage>`.

    :param storage: storage object used as backend
    :type storage: biblib.storage.ReadStorage

    >>> from biblib.storage import FileStorage
    >>> storage = FileStorage('/path/to/some/file')
    >>> db = FileStorage(storage)
    >>> # changes to db will persited within the storage
    >>> db['MyCiteKey'] = someEntry
    >>> # do bulk changes
    >>> with db:
    >>>     # do some changes to db
    >>>
    """

    #: storage given on object creation
    storage = None

    #: flag show if storage is readonly or read/write
    _readOnly = True

    #: flag to signal if object is used as contect manager
    _inContext = False

    def __init__(self, storage, method=None):
        self.storage = storage
        if isinstance(self.storage, bibstorage.WriteStorage):
            self._readOnly = False

        ListOfEntryObj = storage.readEntries().values()
        super(StorageBibDB, self).__init__(ListOfEntryObj, method)

    def __enter__(self):
        self._inContext = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._inContext = False
        if exc_type is None:
            self.save()
            return True
        return False

    def __getitem__(self, ckey):
        try:
            return super(StorageBibDB, self).__getitem__(ckey)
        except KeyError as e:
            entry = self.storage.readEntry(ckey)
            if entry:
                super(StorageBibDB, self).add_entry(entry, ckey)
                return entry
            raise e

    def add_entry(self, entryObj, ckey=None, method=None):
        citeKey = super(StorageBibDB, self).add_entry(entryObj, ckey, method)
        if not self._readOnly and not self._inContext:
            self.storage.createEntry(entryObj, citeKey)

    def __delitem__(self, ckey):
        entry = self.get_entry(ckey)
        super(StorageBibDB, self).__delitem__(ckey)
        if not self._readOnly and not self._inContext:
            self.storage.deleteEntry(entry, ckey)

    def __contains__(self, ckey):
        try:
            self[ckey]
            return True
        except:
            return False

    def mod_entry_type(self, ckey, newtype):
        oldEntry = self.get_entry(ckey)
        super(StorageBibDB, self).mod_entry_type(ckey, newtype)
        if not self._readOnly and not self._inContext:
            newEntry = self.get_entry(ckey)
            self.storage.deleteEntry(oldEntry)
            self.storage.createEntry(newEntry)

    def update_ckey(self, old, new):
        super(StorageBibDB, self).update_ckey(old, new)
        if not self._readOnly and not self._inContext:
            entry = self.get_entry(new)
            self.storage.deleteEntry(entry, old)
            self.storage.createEntry(entry, new)

    def save(self):
        """
        Persist database entries in storage backend
        """
        if not self._readOnly:
            self.storage.writeEntries(self.datadict)


class StringBibDB(StorageBibDB):
    """
    StorageBibDB that will store the database in a BibTex string.

    >>> from biblib.storage import StringStorage
    >>> # get db data as bibtex string
    >>> db.string()
    >>> # or
    >>> str(db)

    :param str string: string from which the db will be initialized
    :param str method: method to determin cite key in db
    :param str mode: open db in read/write ('w') or read onyl ('r') mode
    :param str encoding: string encoding
    """

    def __init__(self, string='', method=None, mode='w', encoding='ascii'):
        if mode == 'w':
            storage = bibstorage.StringStorage(string, encoding)
        else:
            storage = bibstorage.StringReadStorage(string)
        super(StringBibDB, self).__init__(storage, method)

    @property
    def string(self):
        """return storage data as string"""
        return self.storage._src

    def __str__(self):
        return self.string


class FileBibDB(StorageBibDB):
    """
    StorageBibDB that will store the database in a BibTeX file.

    :param str file: path to BibTeX file
    :param str method: method to determin cite key in db
    :param str mode: open db in read/write ('w') or read onyl ('r') mode
    :param str encoding: file encoding
    """

    def __init__(self, filename, method=None, mode='w', encoding='ascii'):
        if mode == 'w':
            storage = bibstorage.FileStorage(filename, encoding)
        else:
            storage = bibstorage.FileReadStorage(filename)
        super(FileBibDB, self).__init__(storage, method)


class SqliteBibDB(StorageBibDB):
    """
    StorageBibDB that will store the database in a SQLite3 database.

    :param str file: path to SQLite database file
    :param str method: method to determin cite key in db
    """

    def __init__(self, filename, method=None):
        super(SqliteBibDB, self).__init__(bibstorage.SqliteStorage(filename), method)


class DoiBibDB(StorageBibDB):
    """
    StorageBibDB that will read entries from doi.org

    :param str method: method to determin cite key in db
    """

    def __init__(self, method=None):
        super(DoiBibDB, self).__init__(bibstorage.DoiReadStorage(), method)



class IsbnBibDB(StorageBibDB):
    """
    StorageBibDB that will read entries for given ISBN numbers

    :param str method: method to determin cite key in db
    """

    def __init__(self, method=None):
        super(IsbnBibDB, self).__init__(bibstorage.IsbnReadStorage(), method)


############################################################################
#
# COLLECTION
#
############################################################################

class DBAccessor(object):

    def __init__(self, dbs=None):
        self._dbs = dbs or []

    def __iter__(self):
        return self

    def __next__(self):
        for key in self.keys():
            yield key

    def next(self):
        return self.__next__()

    def keys(self):
        keys = set()
        for db in self._dbs:
            for key in db.keys():
                if key not in keys:
                    keys.add(key)
                    yield key

    def values(self):
        for key in self.keys():
            yield self[key]

    def items(self):
        for key in self.keys():
            yield key, self[key]

    def __contains__(self, key):
        return any(key in db for db in self._dbs)

    def __getitem__(self, key):
        for db in self._dbs:
            try:
                return db[key]
            except KeyError:
                pass
        raise KeyError()

    def __setitem__(self, key, value):
        self._dbs[0][key] = value

    def __delitem__(self, key):
        for db in self._dbs:
            try:
                del db[key]
                return
            except KeyError:
                pass
        raise KeyError()

    def pop(self, key):
        entry = self[key]
        del self[key]
        return entry

    def __len__(self):
        return len(self.keys())

    def addDB(self, db):
        self._dbs.append(db)


class BibDBCollection(BibDB):


    def __init__(self, dbORentries=None, method=None):

        super(BibDBCollection, self).__init__()

        if isinstance(dbORentries, BibDB):
            db = dbORentries
        else:
            db = BibDB(dbORentries, method)

        self._data = DBAccessor([db])

    @property
    def datadict(self):
        return dict(self.items())

    def addDB(self, db):
        self._data.addDB(db)
