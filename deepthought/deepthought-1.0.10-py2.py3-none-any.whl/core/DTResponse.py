## DTResponse
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

import json

class DTResponse(object):
    obj = None
    err = 0

    def __init__(self,obj=None,err=0):
        self.obj = obj
        self.err = err

    def setResponse(self,obj):
        self.obj = obj

    def error(self,code=None):
        if code is not None:
            self.err = int(code)
        return self.err

    @classmethod
    def objectAsRenderable(self,obj=None):
        renderable = None
        if hasattr(obj,"publicProperties"):
            renderable = obj.publicProperties()
        elif isinstance(obj,list):
            arr = []
            for i in obj:
                arr.append(self.objectAsRenderable(i))
            renderable = arr
        elif isinstance(obj,dict):
            arr = {}
            for k,v in obj.iteritems(): #traverse list
                arr[k] = self.objectAsRenderable(v)
            renderable = arr
        else:
            renderable = obj
        return renderable

    def renderAsDTR(self):
        response = {"fmt":"DTR","err":self.err,"obj":self.objectAsRenderable(self.obj)}
        self.render(json.dumps(response))

    def renderAsJSON(self):
        self.render(json.dumps(self.objectAsRenderable(self.obj)))

    @classmethod
    def render(str):
        ## @todo handle jsonp
        print str

    def respond(self,params={}):
        fmt = params["fmt"] if "fmt" in params else "dtr"
        if fmt is "json":
            self.renderAsJSON()
        else:
            self.renderAsDTR()
