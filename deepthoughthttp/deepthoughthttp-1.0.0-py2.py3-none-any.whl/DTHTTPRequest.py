## DTHTTPRequest
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
# @package Deep Thought (HTTP)
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

import requests

class DTHTTPRequest:
    @classmethod
    def makeHTTPRequest(cls,url,params={},method="GET",cookies={},headers={}):
        if method == "GET":
            r = requests.get(url, cookies=cookies, params=params,headers=headers)
        else: # other methods might need to go into the header?
            r = requests.post(url, cookies=cookies, headers=headers, data=params)
        return r

    @classmethod
    def makeGETRequest(cls,url,params={},cookies={}):
        r = cls.makeHTTPRequest(url,params,"GET",cookies)
        if r is not None and r.status_code == 200:
            return r.text
        return None

    @classmethod
    def makePOSTRequest(cls,url,params={},cookies={}):
        r = cls.makeHTTPRequest(url,params,"POST",cookies)
        if r is not None and r.status_code == 200:
            return r.text
        return None
