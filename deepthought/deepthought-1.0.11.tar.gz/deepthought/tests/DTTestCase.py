## DTTestCase
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

import unittest
from deepthought.store.sqlite.DTSQLiteDatabase import DTSQLiteDatabase
from deepthought.utils.DTLog import DTLog
from deepthought.utils.DTSettingsStorage import DTSettingsStorage

class DTTestCase(unittest.TestCase):
    db = None ## the test store, intialized before each test by +initSQL()+
    production_store = None ## reference to the first production store

    def setUp(self):
        # swap out the production schema for our test schema
        self.production_store = DTSettingsStorage.defaultStore()
        self.db = DTSettingsStorage.defaultStore(DTSQLiteDatabase.init(self.initSQL()))

    ## @return returns +sql+ after adding initialization steps
    def initSQL(self,sql=""):
        return sql

    def testProductionSchema(self):
        if self.production_store is not None:
            test_tables = self.db.allTables()
            prod_tables = self.production_store.allTables()
            for t in test_tables:
                if t in prod_tables: # make sure this table exists in production
                    test_cols = self.db.columnsForTable(t)
                    prod_cols = self.production_store.columnsForTable(t)
                    for c in test_cols:
                        if c not in prod_cols: # make sure all columns exist in production
                            DTLog.warn("'"+self.__class__.__name__+"' is not compatible with production schema (table '{}' missing column '{}')".format(t,c))
                else:
                    DTLog.warn("'"+self.__class__.__name__+"' is not compatible with production schema (missing table '{}')".format(t))
