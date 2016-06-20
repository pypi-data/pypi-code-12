## DTProviderConsumer
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

from .DTConsumer import DTConsumer
from deepthought.utils.DTLog import DTLog

class DTProviderConsumer(DTConsumer):
    def __init__(self,api_name=None,path="",token=None):
        DTConsumer.__init__(self,api_name,path)
        self.sync_token = token

    def handleStatusCodes(self,params,r):
        if r is None:
            return None
        if r.status_code == 200:
            return self.formatResponse(params,r.text)
        elif r.status_code == 278:
            obj = self.formatResponse(params,r.text)
            loc = obj["location"]
            self.redirect(loc,params)
        elif r.status_code == 301 or r.status_code == 302:
            header = r.headers
            self.redirect(header["Location"],params)
        DTLog.error("Failed to access provider ("+str(r.status_code)+"): "+self.url)
        return None

    def preprocessParams(self,params={}):
        params["tok"] = self.upgradeToken(params["tok"] if "tok" in params else self.sync_token)
        if params["tok"] is None:
            raise Exception("Missing required request parameters (tok).")

    def redirect(self,url):
        if True: # if cli
            print "Please visit "+url
            #unimplemented
        elif self.sync_token is not None:
            print ("<script>window.location.href='{}';</script>".format(url))
        else:
            pass #irrelevant

    def upgradeToken(self,consumer_token):
        if self.api.verifyConsumerToken(consumer_token):
            return self.api.providerToken()
        DTLog.warn("Failed to upgrade consumer token ({}).".format(consumer_token))
        if consumer_token == "":
            DTLog.debug("Tip: Did you forget to include the consumer token?")
        return False
