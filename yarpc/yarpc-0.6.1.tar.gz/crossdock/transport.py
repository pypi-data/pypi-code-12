# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from tchannel import TChannel

from yarpc.transport.http import HTTPOutbound
from yarpc.transport.tchannel import TChannelOutbound


HTTP_PORT = 8081
TCHANNEL_PORT = 8082


def factory(server, transport_name):
    if transport_name == 'http':
        return HTTPOutbound('http://%s:%d' % (server, HTTP_PORT))
    elif transport_name == 'tchannel':
        ch = TChannel('client')
        hostport = '%s:%d' % (server, TCHANNEL_PORT)
        return TChannelOutbound(ch, hostport)
    raise Exception('Unrecognized transport_name: %s' % transport_name)
