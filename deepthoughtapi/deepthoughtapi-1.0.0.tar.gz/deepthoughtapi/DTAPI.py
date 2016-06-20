## DTAPI
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

from deepthought.core.DTModel import DTModel
from deepthoughtapi.DTSettingsAPIs import DTSettingsAPIs
from deepthoughthttp.DTSession import DTSession
from deepthought.utils.DTLog import DTLog
import hashlib

class DTAPI(DTModel):
    storage_table = "consumers"

    def __init__(self,params):
        self.name = ""
        self.url = ""
        self.status = 1
        self.consumer_key = None
        self.secret = None
        self.settings = params
        DTModel.__init__(self,params)

    @classmethod
    def fromAPI(cls,api_name):
        settings = DTSettingsAPIs.sharedSettings()
        if api_name not in settings:
            raise Exception("Bad API entry: missing API '{}'".format(api_name))
        if "url" not in settings[api_name]:
            raise Exception("Bad API entry: missing url")
        if "key" not in settings[api_name]:
            raise Exception("Bad API entry: missing key")
        api_url = settings[api_name]["url"]

        settings[api_name]["name"] = api_name
        settings[api_name]["consumer_key"] = settings[api_name]["key"]
        settings[api_name]["url"] = api_url

        return DTAPI(settings[api_name])

    @classmethod
    def consumerTokenForAPI(cls,api_name):
        api = cls.fromAPI(api_name)
        return api.consumerToken()

    def consumerToken(self):
        h = hashlib.md5()
        h.update(self["secret"]+self["consumer_key"]+DTSession.sessionIDForURL(self["url"]))
        s = h.hexdigest()
        return s[0:10]+self["consumer_key"]

    def verifyConsumerToken(self,consumer_token):
        return self.consumerToken() == consumer_token

    def providerToken(self):
        h = hashlib.md5()
        h.update(self["secret"]+self["consumer_key"])
        s = h.hexdigest()
        return s[0:10]+self["consumer_key"]

    def verifyProviderToken(self,token):
        return self.providerToken() == token
