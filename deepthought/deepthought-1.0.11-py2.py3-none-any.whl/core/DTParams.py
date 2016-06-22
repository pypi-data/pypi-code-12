## DTParams
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

from deepthought.utils.DTSettingsStorage import DTSettingsStorage
import dateutil
import json
import re

class DTParams(object):
    params = None
    db = None

    def __init__(self,params=None,db=None):
        self.params = params if params is not None else {} # $_REQUEST...
        self.db = db if db is not None else DTSettingsStorage.defaultStore()

    def __setitem__(self,offset,value):
        if offset is None:
            self.params.append(value)
        else:
            self.params[offset] = value
        return value

    def __contains__(self,offset):
        return offset in self.params

    def __delitem__(self,offset):
        del self.params[offset]

    def __getitem__(self,offset):
        return self.params[offset] if offset in self.params else None

    def param(self,name,default=None):
        return self.params[name] if name in self.params else default

    def jsonParam(self,name,default=None):
        return json.loads(self.params(name,default),True)

    def intParam(self,name,default=None):
        return int(self.params(name,default))

    def doubleParam(self,name,default=None):
        return float(self.param(name,default))

    def boolParam(self,name,default=None):
        return self.parseBool(self.param(name,default))

    def dateParam(self,name,default=None):
        val = self.param(name,default)
        return None if val is "" else self.db.date(dateutil.parser.parse(val))

    def timeParam(self,name,default=None):
        return self.db.time(dateutil.parser.parse(self.param(name,default)))

    def dateTimeParams(self,dateName,timeName,dateDefault=None,timeDefault=None):
        date = self.param(dateName,dateDefault)
        if date is not None:
            return self.db.date(dateutil.parser.parse(date+" "+self.param(timeName,timeDefault)))
        return None

    def checkboxParam(self,name):
        return 1 if name in self.params[name] else 0

    def phoneParam(self,name,default=None):
        m = re.search(r"(\d{3})?[^\d]*(\d{3})[^\d]*(\d{4})",self.params(name,default))
        if m is not None:
            area_code = "" if m.group(1) is "" else "({})".format(m.group(1))
            return "{}{}-{}".format(area_code,m.group(2),m.group(3))
        return ""

    def emailParam(self,name,default=None):
        str = self.parseString(self.param(name,default),self.db)
        ## @todo validate email format
        return str

    def arrayParam(self,name,default=None):
        return self.parseArray(self.param(name,default),self.db)

    def stringParam(self,name,default=None):
        return self.parseString(self.param(name,default),self.db)

    def allParams(self,defaults={}):
        params = defaults
        for k,v in self.params.iteritems():
            if v is None:
                params[k] = None
            elif isinstance(v,list):
                params[k] = self.parseArray(v,self.db)
            ## @todo handle XML?
            else:
                params[k] = self.parseString(v,self.db)
        return params

    @classmethod
    def parseBool(cls,val):
        if isinstance(val,bool):
            return val
        if isinstance(val,basestring):
            val.lower().strip()
        else:
            return val==True
        if val is "true" or val is "t" or val is "yes" or val is "y" or val is "on" or val is "1":
            return True
        if val is "false" or val is "f" or val is "no" or val is "n" or val is "off" or val is "0":
            return False
        return None

    @classmethod
    def parseArray(self,val,db):
        arr = val
        if not isinstance(arr,(dict,list)): # if this isn't array, assume it is json encoded or a single value
            if arr=="":
                return {}
            arr = json.loads(arr)
            if arr is None:
                arr = val
            if not isinstance(arr,(dict,list)): # must have been a single value or ||| separated list
                arr = "|||".split(arr)
        out = {}
        for k,v in arr: #clean all the array params
            if v is None:
                out[k] = "NULL"
            elif isinstance(v,(dict,list)):
                out[k] = self.parseArray(v,db) # recursively parse inner arrays
            ## @todo handle XML
            else:
                out[k] = self.parseString(v,db)
        return out

    def parseString(self,val,db):
        return val if db is None else db.clean(val)
