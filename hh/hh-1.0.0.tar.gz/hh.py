# Copyright (c) 2016 Andrey Torsunov.
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the 
# "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR 
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from enum import Enum


class HttpHeaders(Enum):
    ACCEPT="Accept"
    ACCEPT_CHARSET="Accept-Charset"
    ACCEPT_ENCODING="Accept-Encoding"
    ACCEPT_LANGUAGE="Accept-Language"
    ACCEPT_RANGES="Accept-Ranges"
    AGE="Age"
    ALLOW="Allow"
    AUTHORIZATION="Authorization"
    CACHE_CONTROL="Cache-Control"
    CONNECTION="Connection"
    CONTENT_ENCODING="Content-Encoding"
    CONTENT_LANGUAGE="Content-Language"
    CONTENT_LENGTH="Content-Length"
    CONTENT_LOCATION="Content-Location"
    CONTENT_MD5="Content-MD5"
    CONTENT_RANGE="Content-Range"
    CONTENT_TYPE="Content-Type"
    DATE="Date"
    DAV="Dav"
    DEPTH="Depth"
    DESTINATION="Destination"
    ETAG="ETag"
    EXPECT="Expect"
    EXPIRES="Expires"
    FROM="From"
    HOST="Host"
    IF="If"
    IF_MATCH="If-Match"
    IF_MODIFIED_SINCE="If-Modified-Since"
    IF_NONE_MATCH="If-None-Match"
    IF_RANGE="If-Range"
    IF_UNMODIFIED_SINCE="If-Unmodified-Since"
    LAST_MODIFIED="Last-Modified"
    LOCATION="Location"
    LOCK_TOKEN="Lock-Token"
    MAX_FORWARDS="Max-Forwards"
    OVERWRITE="Overwrite"
    PRAGMA="Pragma"
    PROXY_AUTHENTICATE="Proxy-Authenticate"
    PROXY_AUTHORIZATION="Proxy-Authorization"
    RANGE="Range"
    REFERER="Referer"
    RETRY_AFTER="Retry-After"
    SERVER="Server"
    STATUS_URI="Status-URI"
    TE="TE"
    TIMEOUT="Timeout"
    TRAILER="Trailer"
    TRANSFER_ENCODING="Transfer-Encoding"
    UPGRADE="Upgrade"
    USER_AGENT="User-Agent"
    VARY="Vary"
    VIA="Via"
    WARNING="Warning"
    WWW_AUTHENTICATE="WWW-Authenticate"

    def __get__(self, *args, **kwargs):
        return self.value

    def __str__(self):
        return self.value


H = HttpHeaders
