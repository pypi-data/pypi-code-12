## DTStore
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

import tempfile
import re
import time
from ..store.DTQueryBuilder import DTQueryBuilder
from ..store.DTPreparedQueryBuilder import DTPreparedQueryBuilder

class DTStore(object):
    tables = {} #internal storage for loaded data
    table_types = {} #internal storage for loaded data types
    dsn = None
    readonly = False
    dbname = ""
    ilike = "LIKE" #keyword for case-insensitive search
    col_esc = "\""
    conn = None
    escape = "\\"

    def __init__(self,dsnOrTables={},readonly=False):
        self.readonly = readonly
        if isinstance(dsnOrTables,basestring): # create the store from the specified DSN
            self.connect(dsnOrTables)
        else:
            self.tables = dsnOrTables

    @classmethod
    def init(cls,init_sql=""):
        h,f = tempfile.mkstemp(prefix="dt.store.")
        dsn = "file://"+f
        store = cls(dsn)
        store.connect(dsn)
        store.query(init_sql)
        return store

    def shareTables(self,tables):
        self.tables = tables

    @classmethod
    def copy(cls,store):
        copy = cls(store.tables)
        copy.table_types = store.table_types
        return copy

    @classmethod
    def share(cls,store):
        new = cls()
        new.shareTables(store.tables)
        return new

    def connect(self,dsn):
        pass

    def disconnect(self):
        pass

    def pushTables(self):
        permanent_tables = self.allTables()
        for table, t in self.tables:
            if table not in permanent_tables: #make sure we skip existing tables
                # update types
                row = t[0]
                for k,v in row:
                    if self.table_types[table][k] is None:
                        self.table_types[table][k] = "text"
            self.query(self.tableSQL(table,False,True))

    def tableSQL(self,table,structure_only=False,internal=False):
        t = self.tables[table] if internal else self.select("SELECT * FROM "+table+" "+("LIMIT 1" if structure_only else ""))
        sql = ""
        insert_vals = {}
        insert_cols = {}
        all_cols = self.tables[table][0].keys() if internal else self.columnsForTable(table)
        all_types = self.table_tybles[table] if internal else self.typesForTable(table)
        for row in t:
            vals = {}
            cols = {}
            for c,v in row:
                cols.append(c)
                if isinstance(v,basestring): #do our best to clean what's going in
                    v = self.clean(v)
                vals.append(DTQueryBuilder.formatValue(v)) #collect values
            insert_vals.append(",".join(vals))
            insert_cols.append(",".join(cols))
        # create the table
        create_cols = ",".join(map(lambda c: "{}{}{} {}".format(self.col_esc,c,self.col_esc,all_types[c]),all_cols))
        sql += "CREATE TABLE \"{}\" ({});\n".format(table,create_cols)
        # insert all rows (can't use prepared, cause we don't know how many cols)
        if not structure_only:
            for i,row in t:
                sql += "INSERT INTO \"{}\" ({}) VALUES ({});\n".format(table,insert_cols[i],insert_vals[i])
        return sql

    def pullTables(self):
        if self.tables is not None and self.tables.count() > 0:
            return False
        for table in self.allTables(): #for each table in the database
            self.pullTable(table)

    def pullTable(self,table):
        self.tables[table] = self.select("SELECT * FROM "+table)
        self.table_types[table] = self.typesForTable(table)

    def purgeTable(self,table):
        del self.tables[table]
        del self.table_types[table]

## @name Query methods
## @{
    def clean(self,val):
        pass

    def unescape(self,val):
        return re.sub(r""+self.escape+"(.)","\\1",val)

    def query(self,stmt):
        pass

    def select(self,stmt):
        pass

    def lastInsertID(self):
        pass

    def columnsForTable(self,table_name):
        pass

    def typeForColumn(self,table_name,column_name):
        return "text"

    def typesForTable(self,table_name):
        out = {}
        for cV in self.columnsForTable(table_name):
            out[cV] = "text"
        return out

    def allTables(self):
        pass

    def select1(self,stmt):
        rows = self.select(stmt)
        return rows[0] if len(rows) > 0 else None

    def selectAs(self,stmt,cls):
        list = []
        rows = self.select(stmt)
        for r in rows:
            obj = cls(r)
            list.append(obj)
            obj.setStore(self) # keep track of where we came from
        return list

    def selectKV(self,stmt):
        list = []
        rows = self.select(stmt)
        if rows.count() > 0:
            cols = rows[0].keys()
            key_col = cols[0]
            val_col = cols[1]
            for r in rows: #pair keys and values
                list[r[key_col]] = r[val_col]
        return list

    def insert(self,stmt):
        self.query(stmt)
        return self.lastInsertID()

    def insertEmpty(self,table):
        return self.insert("INSERT INTO "+table+" DEFAULT VALUES")

    def prepareStatement(self,query,name=None):
        pass

    def placeholder(self,params,val):
        pass

    def execute(self,stmt,params={}):
        pass
## @}

## @name Query Builder methods
## @{
    def qb(self):
        return DTQueryBuilder(self)

    def where(self,where_str):
        return self.filter().where(where_str)

    def filter(self,filter={}):
        qb = self.qb()
        return qb.filter(filter)

    def prepare(self,stmt_name=None):
        return DTPreparedQueryBuilder(self,stmt_name)
## @}

## @name Transaction methods
## @{
    def begin(self):
        self.query("BEGIN")

    def commit(self):
        try:
            self.query("COMMIT")
        except:
            pass #ignore the commit if a transaction wasn't started

    def rollback(self):
        self.query("ROLLBACK")
## @}

## @name Date methods
## @{
    def now(self):
        return self.gmdate()

    def day(self,timestamp=None):
        timestamp = timestamp if timestamp is not None else time.time()
        return time.date("Y-m-d e",timestamp)

    def date(self,timestamp=None):
        timestamp = timestamp if timestamp is not None else time.time()
        return time.date("Y-m-d H:i:s e",timestamp)

    def gmdate(self,timestamp=None):
        timestamp = timestamp if timestamp is not None else time.time()
        return time.gmdate("Y-m-d H:i:s e",timestamp)

    def time(self,timestamp=None):
        timestamp = timestamp if timestamp is not None else time.time()
        return time.date("H:i:s",timestamp)

    def localizedDate(self,timestamp=None):
        return time.strftime("%x",timestamp)

    def localizedTime(self,timestamp=None):
        return time.strftime("%X",timestamp)

    def __destruct__(self):
        try:
            self.disconnect()
        except:
            pass
## @}
