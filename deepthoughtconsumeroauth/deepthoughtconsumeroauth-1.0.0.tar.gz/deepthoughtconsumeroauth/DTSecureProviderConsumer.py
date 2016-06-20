## DTSecureProviderConsumer
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
# @package Deep Thought (Consumer-OAuth)
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

from deepthoughthttp.DTSession import DTSession
from deepthoughtconsumer.DTProviderConsumer import DTProviderConsumer
from deepthought.utils.DTLog import DTLog
import requests
from urlparse import parse_qs
from requests_oauthlib import OAuth1

class DTSecureProviderConsumer(DTProviderConsumer):
    def __init__(self,api_name,path,token=None):
        DTProviderConsumer.__init__(self,api_name,path,token)
        self.oauth = OAuth1(self.api["consumer_key"],client_secret = self.api["secret"])
        self.session = DTSession.sharedSession()

    def sendRequestToProvider(self,url,params,method="POST",multipart=False):
        r = requests.post(url=url,data=params,auth=self.oauth)
        return r.content

    def request(self,action,params={},method="POST"):
        url = self.url
        if self.action_format=="suffix":
            url += action
        params[self.action_format] = action # we need to do this either way to satisfy the verification
        if self.accessToken() is not None: #we've got the access token, just make the request already!
            if "tok" not in params or self.action_format not in params:
                raise Exception("Missing required request parameters (tok,act).")

            self.oauth = OAuth1(self.api["consumer_key"],
            client_secret=self.api["secret"],
            resource_owner_key=self.accessToken(),
            resource_owner_secret=self.accessTokenSecret())
            return self.formatResponse(params,self.sendRequestToProvider(url,params,method))
        else:
            if False and "oauth_verifier" in self.session: # session doesn't exist yet... because it will never exist
                self.oauthAccessToken()
                self.sync_token = "fogeddabaddit" #don't try to redirect us async-style--we got here via provider
                self.redirect(self.session[self.api["name"]+"_oauth_origin"])
            else:
                self.oauthRequestToken()
                #self.redirect("{}?oauth_token={}".format(self.session["oauth_login_url"],self.requestToken()))

    def oauthRequestToken(self):
        r = requests.post(url=self.url+"?act=request_token",auth=self.oauth)
        credentials = parse_qs(r.content)
        self.setRequestToken(credentials.get("oauth_token")[0],credentials.get("oauth_token_secret")[0])
        if credentials.get("login_url") is not None:
            self.session["oauth_login_url"] = credentials.get("login_url")[0]
        else:
            DTLog.error("No login url returned.")
        print 'Please go here and authorize,',"{}?oauth_token={}".format(self.session["oauth_login_url"],self.requestToken())
        verifier = raw_input('Please input the verifier (none): ')
        self.session["oauth_verifier"] = verifier #not sure what to do here...
        self.oauthAccessToken()
        #self.session[self.api["name"]+"_oauth_origin"] = verifier

    def oauthAccessToken(self):
        access_token_url = self.url+"?act=access_token"
        token = self.requestToken()
        secret = self.requestTokenSecret()
        self.oauth = OAuth1(self.api["consumer_key"],
            client_secret=self.api["secret"],
            resource_owner_key=token,
            resource_owner_secret=secret,
            verifier = self.session["oauth_verifier"]
        )
        r = requests.post(url=access_token_url,auth=self.oauth)
        credentials = parse_qs(r.content)
        self.setAccessToken(credentials.get("oauth_token")[0],credentials.get("oauth_token_secret")[0])
        del self.session[self.api["name"]+"_oauth_request_token"]
        del self.session[self.api["name"]+"_oauth_request_secret"]

    def accessToken(self):
        return self.session[self.api["name"]+"_oauth_access_token"]

    def accessTokenSecret(self):
        return self.session[self.api["name"]+"_oauth_access_secret"]

    def setAccessToken(self,key,secret):
        self.session[self.api["name"]+"_oauth_access_token"] = key
        self.session[self.api["name"]+"_oauth_access_secret"] = secret

    def requestToken(self):
        return self.session[self.api["name"]+"_oauth_request_token"]

    def requestTokenSecret(self):
        return self.session[self.api["name"]+"_oauth_request_secret"]

    def setRequestToken(self,key,secret):
        self.session[self.api["name"]+"_oauth_request_token"] = key
        self.session[self.api["name"]+"_oauth_request_secret"] = secret
