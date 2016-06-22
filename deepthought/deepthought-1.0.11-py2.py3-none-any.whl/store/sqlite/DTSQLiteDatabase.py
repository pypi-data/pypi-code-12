## DTSQLiteDatabase
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


from ..DTStore import DTStore
from urlparse import urlparse
import sqlite3
import re
import tempfile
from deepthought.utils.DTLog import DTLog

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DTSQLiteDatabase(DTStore):
    def connect(self,dsn):
        parts = urlparse(dsn)
        database = parts.path
        self.conn = sqlite3.connect(database)
        self.conn.row_factory = dict_factory
        #self.conn.createFunction('LEVENSHTEIN', 'DTSQLiteDatabase::levenshtein', 2)

    #@staticmethod
    #def levenshtein(a,b):
    #    return levenshtein(a,b)

    def select(self,stmt):
        result = self.conn.execute(stmt)
        if result is False:
            DTLog.error(DTLog.colorize(self.conn.lastErrorMsg(),"error")+"\n"+stmt)
            return []
        return result.fetchall()

    def query(self,stmt):
        if self.conn.executescript(stmt) is False:
            raise Exception(DTLog.colorize(self.db.lastErrorMsg(),"error")+"\n"+stmt)

    @staticmethod
    def clean(val):
        return re.sub(r"([^\\])'", "\g<1>''", str(val))

    def disconnect(self):
        if self.conn is None:
            raise Exception("Attempt to disconnect an nonexistent connection.")
        if self.conn.close() is False:
            raise Exception(DTLog.colorize(self.conn.lastErrorMsg(),"error")+"\n")

    def lastInsertID(self):
        row = self.select1("SELECT last_insert_rowid() as id")
        return row["id"]

    def insert(self,stmt):
        self.query(stmt)
        return self.lastInsertID()

    def placeholder(self,params,val):
        params.append(val)
        i = len(params)
        return ":"+str(i)

    def prepareStatement(self,stmt,name=None):
        h,f = tempfile.mkstemp()
        name = name if name is not None else "DT_prepared_"+f
        return stmt,name
        #return self.conn.prepare()

    def execute(self,stmt,params=[]):
        rows = []
        result = self.conn.execute(stmt,params)
        if result is False:
            raise Exception(DTLog.colorize(self.conn.lastErrorMsg(),"error"))
            return rows
        row = result.fetchone()
        while row:
            rows.append(row)
            row = result.fetchone()
        return rows

    def columnsForTable(self,table):
        out = []
        cols = self.select("PRAGMA table_info(`{}`)".format(table))
        for c in cols:
            out.append(c["name"])
        return out

    def typeForColumn(self,table_name,column_name):
        types = self.typesForTable(table_name)
        if types[column_name] is not None:
            return types[column_name]
        return "text"

    def typesForTable(self,table_name):
        out = []
        cols = self.select("PRAGMA table_info(`{}`)".format(table_name))
        for c in cols:
            out.append(c["type"])
        return out

    def allTables(self):
        out = []
        rows = self.select("SELECT name FROM sqlite_master WHERE type='table';")
        for r in rows:
            if r["name"] != "sqlite_sequence":
                out.append(r["name"])
        return out
