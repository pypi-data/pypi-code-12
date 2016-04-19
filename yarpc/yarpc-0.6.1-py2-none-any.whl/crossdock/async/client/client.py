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

import json

from tornado import gen
from tornado.web import Application, RequestHandler

from . import behavior

BEHAVIORS = {
    'raw': behavior.raw,
    'json': behavior.json,
    'thrift': behavior.thrift,
}

PASSED = 'passed'
SKIPPED = 'skipped'
FAILED = 'failed'


def start():
    harness = Application([
        (r"/", TestCaseHandler),
    ], debug=True)
    harness.listen(8080, '0.0.0.0')


class TestCaseHandler(RequestHandler):

    def head(self):
        """Crossdock makes a HEAD request to see when client is ready."""
        pass

    @gen.coroutine
    def get(self):
        """Crossdock sends GET requests with query params to initiate test."""
        behavior = self.get_query_argument('behavior')
        server = self.get_query_argument('server')
        transport = self.get_query_argument('transport')

        fn = BEHAVIORS.get(behavior)

        if fn is None:
            self.write(json.dumps([{
                "status": SKIPPED,
                "output": "Not implemented",
            }]))
            return

        try:
            resp = yield gen.maybe_future(fn(server, transport))
            self.write(json.dumps([{
                "status": PASSED,
                "output": resp
            }]))
        except Exception as e:
            self.write(json.dumps([{
                "status": FAILED,
                "output": "%s" % e
            }]))
            return
