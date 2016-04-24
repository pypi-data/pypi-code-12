'''
Copyright 2016 define().

This file is part of dsgnutils.

dsgnutils is free software: you can redistribute it and/or modify it under the
terms of the Lesser GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

dsgnutils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the Lesser GNU General Public License for more
details.

You should have received a copy of the Lesser GNU General Public License along
with dsgnutils.  If not, see <http://www.gnu.org/licenses/>.
'''

from dsgnutils.always import *
from dsgnutils.utils import *

#=======DIMENTIONAL DATABASE OBJECTS==========================================
class DimentionalDB(object):
    def __init__(self):
        pass
    def massageQuery(self,arg):
        ret=re.sub('\n',' ',arg)
        ret=re.sub('\t',' ',ret)
        ret=re.sub(r' +',' ',ret)
        ret=re.sub(r'^ ','',ret)
        ret=re.sub(r'\( ','(',ret)
        ret=re.sub(r' \)',')',ret)
        return ret
    def c(self,cmd):
        pass
    def q0(self,q):
        pass
    def q1(self,q):
        pass
    def q2(self,q):
        pass

import sqlite3
class SqliteDB(DimentionalDB):
    '''
        not all purpose; for simple, small information retrieval
    '''
    def __init__(self,dbname,verbose=False):
        self.connString=getFile(dbname)
        self.verbose=verbose
    def massageQuery(self,arg):
        ret=super().massageQuery(arg)
        ret=re.sub('%s','?',ret)
        return ret
    def ex(self,q,params=None,schema=None):
        '''returns dict'''
        ret={}
        q=self.massageQuery(q)
        if self.verbose:
            pErr(q,self)
        params=() if not params else params
        conn=sqlite3.connect(self.connString)
        conn.row_factory=sqlite3.Row
        cursor=conn.cursor()
        cursor.execute(q,params)
        ret={'query':q,'rows':cursor.rowcount}
        cursor.close()
        conn.commit()
        conn.close()
        return ret
    def q2(self,q,params=None,schema=None):
        '''returns empty list  or list of dict'''
        ret=[]
        q=re.sub('%s','?',q)
        params=() if not params else params
        conn=sqlite3.connect(self.connString)
        conn.row_factory=sqlite3.Row
        cursor=conn.cursor()
        cursor.execute(q,params)
        rslt=cursor.fetchall()
        if rslt:
            for x in rslt:
                dic={}
                for k in x.keys():
                    dic[k]=x[k]
                ret.append(dic)
        cursor.close()
        conn.close()
        return ret
    def q1(self,q,params=None,schema=None):
        '''returns None or dict'''
        ret=self.q2(q,params,schema)
        if ret:
            assert(1==len(ret))
        ret=None if not ret else ret[0]
        return ret

#import psycopg2
#import psycopg2.extras
#class PostgresDB(DimentionalDB):
#    '''not all purpose; for simple, small information retrieval'''
#    def __init__(self,host,port,dbname,user,pgpass):
#        pwd=[
#            x[4]
#            for x in readCSV(pgpass,delim=':')
#            if (
#                    x[0] in ['*',host]
#                and x[1] in ['*',port]
#                and x[2] in ['*',dbname]
#                and x[3] in ['*',user]
#            )
#        ]
#        assert(pwd)
#        sIo=StringIO()
#        sIo.write("host='%s'"%(host))
#        sIo.write(" port=%s"%(port))
#        sIo.write(" dbname='%s'"%(dbname))
#        sIo.write(" user='%s'"%(user))
#        sIo.write(" password='%s'"%(pwd[0]))
#        self.connString=sIo.getvalue()
#    def q2(self,q,params=None,schema=None):
#        ret=[]
#        conn=psycopg2.connect(
#            self.connString,
#            cursor_factory=psycopg2.extras.RealDictCursor
#        )
#        cursor=conn.cursor()
#        if schema:
#            cursor.execute("set search_path=%s",(schema,))
#        cursor.execute(q,params)
#        ret=cursor.fetchall()
#        cursor.close()
#        conn.close()
#        return ret
#    def q1(self,q,params,schema):
#        ret=self.q2(q,params,schema)
#        if None!=ret:
#            assert(1==len(ret))
#        ret=None if not ret else ret[0]
#        return ret



