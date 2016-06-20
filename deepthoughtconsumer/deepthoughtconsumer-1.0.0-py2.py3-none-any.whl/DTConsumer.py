## DTBasicConsumer
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
# @package Deep Thought (Consumer)
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

from deepthoughtapi.DTAPI import DTAPI
from deepthought.utils.DTLog import DTLog
from deepthought.core.DTResponse import DTResponse
from deepthoughthttp.DTHTTPRequest import DTHTTPRequest
from deepthoughthttp.DTSession import DTSession
import re
import json

class DTConsumer(object):
    def __init__(self,api_name=None,path=""):
        self.api = None
        self.url = None
        self.default_method = "POST"
        self.err = None
        if api_name is not None: # load the api from storage
            self.loadAPI(DTAPI.fromAPI(api_name),path)

    def loadAPI(self,api,path=""):
        self.api = api
        self.url = self.api["url"]+path
        self.action_format = self.api["settings"]["action"] if "action" in self.api["settings"] else "act"

    def preprocessParams(self,params = {}):
        pass

    def handleStatusCodes(self,params,r):
        if r is None:
            return None
        if r.status_code == 200:
            return self.formatResponse(params,r.text)
        DTLog.error("Failed to access provider ("+str(r.status_code)+"): "+self.url)
        return None

    def request(self,action,params={},method=None):
        if method is None:
            method = self.default_method
        session = DTSession.sharedSession() #have to start the session
        url = self.url
        if self.action_format == "suffix":
            url += action
        else:
            params[self.action_format] = action
        self.preprocessParams(params)
        # this cookie parameter is essential for getting the same session with each request (whether this *should be done for public APIs is another question...)
        r = DTHTTPRequest.makeHTTPRequest(url,params,method,session[self.api["name"]+"_cookies"])
        return self.handleStatusCodes(params,r)

    def formatResponse(self,params,response):
        response = response if not "callback" in params else re.sub(params["callback"]+r"\(\s*(.*?)\s*\)$","\1").strip()
        fmt = params["fmt"] if "fmt" in params else None
        if fmt is None and "format" in params:
            fmt = params["format"]
        if fmt == "html":
            return response
        else:
            response = json.loads(response)
            if "fmt" in response and response["fmt"] == "DTR":
                self.err = response["err"] if "err" in response else 0 # carry the response code from the provider
                return response["obj"] if response is not None else ""
        return response

    def requestAndRespond(self,params,method=None):
        if method is None:
            method = self.default_method
        action = params["act"] if "act" in params else None #these can be (correctly) omitted, for example during authentication at oauth_verifier
        response = DTResponse(self.request(action,params,method))
        response.error(self.err)
        response.respond(params)
        return response
