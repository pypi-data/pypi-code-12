## DTSettingsStorage
#
# Copyright (c) 2016, Expressive Analytics, LLC <info@expressiveanalytics.com>.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# @package Deep Thought
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

from .DTSettings import DTSettings
from deepthought.store.sqlite.DTSQLiteDatabase import DTSQLiteDatabase
from deepthought.store.mysql.DTMySQLDatabase import DTMySQLDatabase
from deepthought.store.pgsql.DTPgSQLDatabase import DTPgSQLDatabase
import json


named_stores = {
    "DTSQLiteDatabase":DTSQLiteDatabase,
    "DTMySQLDatabase":DTMySQLDatabase,
    "DTPgSQLDatabase":DTPgSQLDatabase
}

class DTSettingsStorage(DTSettings):
    _shared_storage = {}
    _storage_connections = {} # internal storage for singleton storage connections
    _default_store = None

    @classmethod
    def initShared(cls,path):
        cls._storage_connections = {} # clear this out for new storage
        cls._shared_storage = json.load(open(path))
        return cls._shared_storage

    @classmethod
    def sharedSettings(cls,settings=None):
        if settings is not None:
            cls._shared_storage.update(settings)
        return cls._shared_storage

    @classmethod
    def connect(cls,store):
        if store not in cls._storage_connections or cls._storage_connections[store].conn is None:
            storage = cls.sharedSettings()
            if storage is None or store not in storage:
                raise Exception("Connection '"+store+"' not found in storage!")
            connector = storage[store]["connector"]
            dsn = storage[store]["dsn"]
            readonly = storage[store]["readonly"] if "readonly" in storage[store] else False
            cls._storage_connections[store] = named_stores[connector](dsn,readonly)
        return cls._storage_connections[store]

    @classmethod
    def defaultStore(cls,default=None):
        if default is not None:
            cls._default_store = default
            return cls._default_store
        if cls._default_store is None:
            storage = cls.sharedSettings()
            if len(storage)==0:
                return None
            store_names = storage.keys()
            cls._default_store = cls.connect(store_names[0])
        return cls._default_store
