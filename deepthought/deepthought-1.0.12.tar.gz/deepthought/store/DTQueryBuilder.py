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

from ..utils.DTLog import DTLog
import json
import re

class DTQueryBuilder(object):

    def __init__(self,db):
        self.db = db
        self.from_clause = None
        self.join_clause = ""
        self.group_by = ""
        self.where_clause = "1=1"
        self.having_clause = ""
        self._enforce = None
        self.filter_dict = None
        self.limit_clause = ""
        self.order_by = ""
        self.columns = []

    def where(self,where_str):
        if self.where_clause is not "1=1":
            DTLog.warn("WHERE clause overridden! Did you mean to use enforce? '{}' => '{}'".format(self.where_clause,where_str))
        self.where_clause = where_str
        return self

    def buildWhereClause(self):
        wc = "({}) AND".format(self._enforce) if self._enforce is not None else "({})".format(self.where_clause) #ALWAYS wrap the where clause, or it conflicts with enforce (e.g. [enforcer] and "name like 'a' OR name like 'b'")
        if self.filter_dict is not None and len(self.filter_dict) > 0:
            arr = []
            for k,v in self.filter_dict.iteritems():
                arr.append(self.renderKV(k,v))
            return wc+" AND "+" AND ".join(arr)
        return wc

    @classmethod
    def renderKV(cls,k,v):
        if v is None: #handle null-matching
            return k+" IS NULL"
        if isinstance(v,list): #in the case of an array, the elements are [op,exp,txfunc]
            if isinstance(v[1],list):
                val = "("+",".join(map(lambda v: cls.formatValue(v),v[1]))+")"
            elif v[1]=="NULL":
                val = "NULL"
            else:
                val = cls.formatValue(v[1])
            if len(v) > 2: #check for transform function
                val = v[2]+"("+v+")"
            return "{} {} {}".format(k,v[0],val)
        return str(k)+"="+cls.formatValue(v)

    def filter(self,params=None):
        if params is None:
            return self.filter_dict
        if self.filter_dict is None:
            self.filter_dict = {}
        self.filter_dict.update(params)
        return self

    def enforce(self,enforce_str):
        if self._enforce is not None:
            DTLog.warn("ENFORCER overridden: '{}' => '{}'".format(self._enforce,enforce_str))
        self._enforce = enforce_str
        return self

    def fail(self):
        self.filter_dict = {"1":0} # 1 == 0 always fails
        return self

    def addColumns(self,cols):
        if isinstance(cols,dict):
            cols = map(lambda k,v: v+" as "+k,cols.keys(),cols.values())
        self.columns += cols
        return self

    def fromT(self,from_str=None):
        if from_str is None:
            return self.from_clause
        self.from_clause = from_str
        return self

    def nestAs(self,cols="*",alias=""):
        qb = self(self.db)
        from_str = "("+self.selectStatement(cols)+") as "+alias
        qb.fromT(from_str)
        return qb

    def limit(self,limit_count):
        self.limit_clause = "LIMIT "+str(limit_count)
        return self

    def join(self,table,condition):
        self.join_clause += " JOIN {} ON ({})".format(table,condition)
        return self

    def leftJoin(self,table,condition):
        self.join_clause += " LEFT JOIN {} ON ({})".format(table,condition)
        return self

    def groupBy(self,group_str):
        self.group_by = "GROUP BY "+group_str
        return self

    def orderBy(self,order_str):
        self.order_by = "ORDER BY "+order_str
        return self

    def having(self,having_str):
        self.having_clause = "HAVING ({})".format(having_str)
        return self

    def select(self,cols="*"):
        stmt = self.selectStatement(cols)
        return self.db.select(stmt)

    def selectKV(self,cols="*"):
        stmt = self.selectStatement(cols)
        return self.db.selectKV(stmt)

    def selectStatement(self,cols="*"):
        column_clause = cols
        if len(self.columns) > 0:
            column_clause += ", "+",".join(self.columns)
        return "SELECT {} FROM {} {} WHERE {} {} {} {} {}".format(
            column_clause,
            self.from_clause, self.join_clause,
            self.buildWhereClause(),
            self.group_by, self.having_clause,
            self.order_by, self.limit_clause
        )

    def count(self,cols="*"):
        stmt = self.nestAs(cols,"dt_countable").selectStatment("COUNT(*) as count")
        row = self.db.select1(stmt)
        return row["count"]

    def sum(self,col):
        row = self.select1("SUM("+col+") as total")
        return row["total"]

    def select1(self,cols="*"):
        self.limit("1")
        stmt = self.selectStatement(cols)
        rows = self.db.select(stmt)
        if len(rows) > 0:
            return rows[0]
        return None

    def selectAs(self,cls,cols="*"):
        stmt = self.selectStatement(cols)
        return self.db.selectAs(stmt,cls)

    def update(self,properties):
        if len(properties) > 0:
            col_esc = self.db.col_esc
            set_str = ",".join(map(lambda k,v:
                "{}{}{}=".format(col_esc,k,col_esc)+self.formatValue(v),
                properties.keys(),
                properties.values()))
            stmt = "UPDATE {} SET {} WHERE ".format(self.from_clause,set_str)+self.buildWhereClause()
            self.db.query(stmt)
            return True
        return False

    def insert(self,properties):
        if len(properties) > 0:
            cols_str = ",".join(properties.keys())
            vals_str = ",".join(map(lambda v:self.formatValue(v),properties.values()))
            stmt = "INSERT INTO {} ({}) VALUES ({});".format(self.from_clause,cols_str,vals_str)
            return self.db.insert(stmt)
        return self.db.insertEmpty(self.from_clause)

    def delete(self):
        try:
            stmt = "DELETE FROM "+self.from_clause+" WHERE "+self.buildWhereClause()
            self.db.query(stmt)
            return True
        except:
            pass
        return False

    @classmethod
    def formatValue(self,v):
        if v is None or v is "NULL":
            return "NULL"
        elif not isinstance(v,basestring):
            return "'"+json.dumps(v)+"'"
        elif re.match(r"\\DTSQLEXPR\\",v): #handle expressions as literals, as long as params are cleand, this should never be possible from users because of the unescaped backslash
            return v[11:]
        return "'"+str(v)+"'" # ALWAYS quote other values to avoid 'id=1 OR 1=1' attacks

    def __str__(self):
        return self.selectStatement()
