# -*- coding: utf-8 -*-
"""
ThisThis module contains the BibTeX file class.

"""
from __future__ import print_function

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__ = filter(str.isdigit, "$Revision: 217 $")


# import external package modules
from magic import Magic
import os
import shutil

# import of internal package modules
from ._bibdb import BibDB
import biblib


class BibTexFile(BibDB):
    """

    This is the BibTeX file class.

    It is derived from the :class:`.BibDB` class including a reader :func:`.db_from_file`
    and writer :func:`.db_to_file` function.
    It also supports the ``with`` statement.

    :param filename: input BibTeX file
    :type filename: str
    :return: BibTeX file object
    :rtype: .BibTexFile
    """

    def __init__(self, filename):
        # call parent init
        super(BibTexFile, self).__init__()
        # set filename
        self.bibFile = filename
        self.max_backup = 10
        # check file
        self._check_file()
        # load file
        self.reload()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if not exception_type:
            self.save()

    def _check_file(self):
        self.absFilePath = os.path.abspath(self.bibFile)
        self.filePath, self.fileName = os.path.split(self.absFilePath)
        self.readonly = False
        self.newfile = False
        # check if folder exists
        if not os.path.exists(self.filePath):
            print('Path \'' + self.filePath + '\' did not exist!')
            raise IOError
        # check if file exists
        if not os.path.isfile(self.absFilePath):
            print('File \'' + self.absFilePath + '\' did not exist!')

            if not os.access(self.filePath, os.W_OK):
                print('Path \'' + self.filePath + '\' is not writeable!')
                raise IOError
            else:
                print('File \'' + self.absFilePath + '\' created!')
                #os.mknod( self.absFilePath )
                self.fileEncoding = 'ascii'
                self.newfile = True
                return
        else:
            if not os.access(self.absFilePath, os.R_OK):
                print('File \'' + self.absFilePath + '\' is not readable!')
                raise IOError

            if not os.access(self.absFilePath, os.W_OK):
                print('File \'' + self.absFilePath + '\' is not writeable!')
                self.readonly = True
        # determine the encoding of the file
        mm = Magic(mime_encoding=True)
        self.fileEncoding = mm.from_file(self.absFilePath)

    def reload(self):
        """
        Reload the BibTeX file.

        .. note:: The database will overwritten and all changes will get lost!
        """
        # initiate / clear entry data
        self._data = {}
        if not self.newfile:
            # read file and add entry data
            dbObj = biblib.db_from_file(self.bibFile)
            self.merge_bibdb(dbObj, method=None)
        # (re-)hash
        self.initHash = self.__hash__()

    def save(self):
        """
        Save all changes to the BibTeX file.
        """
        # check if file writeable
        if self.readonly:
            return False
        # check if file has changed
        if self.initHash == self.__hash__():
            return False
        # backup file
        if not self.newfile:
            self._backup()
        # write to file
        biblib.db_to_file(self, self.absFilePath, encoding=self.fileEncoding)
        self.newfile = False
        # (re-)hash
        self.initHash = self.__hash__()

    def _backup(self):
        """
        Backup a file and its previous backups.
        """
        bflist = [self.fileName, self.fileName + '.bak']
        for i in range(1, self.max_backup):
            bflist.append(self.fileName + '.bak.' + str(i))
        for i in range(2, len(bflist) + 1):
            bf0 = os.path.join(self.filePath, bflist[-i])
            bf1 = os.path.join(self.filePath, bflist[-i + 1])
            if os.path.isfile(bf0):
                shutil.copy2(bf0, bf1)

    def has_changed(self):
        """
        Check if database have changed (since last saving).

        :return: *True* | *False*
        :rtype: bool
        """
        return self.initHash != self.__hash__()

    def close(self):
        """
        Alternative to the :meth:`.BibTexFile.save` function.
        """
        self.save()

#==============================================================================


class BibTexFileSet(object):

    def __init__(self):

        # initiate variables
        # Dictionary key -> alias and value -> BibTexFile object
        self._data = {}

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        """
        Returns a list of alias defined in the set.

        :return: list of alias
        :rtype: list
        """
        return self._data.keys()

    def values(self):
        """
        Returns a list of BibTexFile object stored in the set.

        :return: list of BibTexFile object
        :rtype: list
        """
        return self._data.values()

    def items(self):
        """
        Returns a list of sets containing alias/ BibTexFile object.

        :return: list of sets alias/ BibTexFile object
        :rtype: list
        """
        return self._data.items()

    def __getitem__(self, key):
        """
        Returns the BibTexFile object with the given alias in the set.

        :param key: alias
        :type key: str
        :return: BibTeX file object
        :rtype: .BibTexFile
        :raises NameError: if alias did not exist in set
        """
        if not self._data.has_key(key):
            msg = 'Alias "' + key + '" did not exists in set!'
            raise NameError(msg)
        return self._data[key]

    def __setitem__(self, key, value):
        """
        Add/set a BibTeX file object with an alias to the set.

        :param key: alias
        :type key: str
        :param value: BibTeX file object
        :type value: .BibTexFile
        :raises TypeError: if value is not of a valid object type
        :raises KeyError: if alias already exists in set
        """

        # check if it is a valid object type
        if not isinstance(value, BibTexFile):
            msg = 'Value (object) is of wrong type!'
            raise TypeError(msg)

        if key in self._data.keys():
            msg = 'Alias "' + key + '" already exists in set!'
            raise KeyError(msg)

        self._data[key] = value

    def __delitem__(self, key):
        """
        Deletes a BibTeX file object from the set.

        :param key: alias
        :type key: str
        :raises NameError: if citation-key did not exist in database
        """
        if key not in self._data.keys():
            msg = 'Alias "' + key + '" did not exists in set!'
            raise NameError(msg)
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def add_file(self, filename, alias=None):
        btfileObj = BibTexFile(filename)
        if not alias:
            key = btfileObj.fileName
        else:
            key = alias
        self[key] = btfileObj
        return key

    def has_doi(self, doi):
        """
        Check if a given DOI is known.

        :param doi: digital object identifier (DOI)
        :type doi: str
        :return: True | False
        :rtype: bool
        """
        if doi in self.dois:
            return self.dois[doi]
        else:
            return False

    def __contains__(self, key):
        return key in self.ckeys.keys()

    @property
    def dois(self):
        """
        Returns a dictionary with *doi* as key and [alias, citation-key] list as value.
        """
        out = {}
        for alias, btfileObj in self.items():
            for doi, ckey in btfileObj.dois.items():
                out[doi] = [alias, ckey]
        return out

    @property
    def ckeys(self):
        """
        Returns a dictionary with *citation-key* as key and alias as value.
        """
        out = {}
        for alias, btfileObj in self.items():
            for ckey in btfileObj.ckeys:
                out[ckey] = alias
        return out
