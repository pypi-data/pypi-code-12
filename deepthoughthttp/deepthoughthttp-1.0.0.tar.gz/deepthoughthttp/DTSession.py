## DTSession
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

from deepthought.core.DTModel import DTModel
from urlparse import urlparse
import requests

class DTSession(DTModel):
    _shared_session = None
    _session_started = False
    _remote_session_ids = {}

    def __init__(self,paramsOrQuery=None):
        self.startSession()
        if paramsOrQuery is None:
            paramsOrQuery = {}
        DTModel.__init__(self,paramsOrQuery)

    @classmethod
    def startSession(cls):
        if not cls._session_started:
            pass # python doesn't have sessions, silly (@todo... create connector for django)
        cls._session_started = True

    @classmethod
    def sharedSession(cls):
        if cls._shared_session is None:
            cls._shared_session = cls()
        return cls._shared_session

    @classmethod
    def destroy(cls):
        cls._shared_session = None
        cls._session_started = False

    @classmethod
    def sessionIDForURL(cls,url):
        parts = urlparse(url)
        host = parts.netloc
        if host not in cls._remote_session_ids:
            r = requests.get(url)
            cls._remote_session_ids[host] = r.cookies["PHPSESSID"]
        return cls._remote_session_ids[host]
