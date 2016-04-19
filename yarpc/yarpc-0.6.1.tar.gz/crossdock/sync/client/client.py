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

from flask import Flask, request

from . import behavior

BEHAVIORS = {
    'raw': behavior.raw,
    'json': behavior.json,
    'thrift': behavior.thrift,
}

PASSED = 'passed'
SKIPPED = 'skipped'
FAILED = 'failed'


app = Flask(__name__)


@app.route('/', methods=['HEAD'])
def ready():
    """Crossdock makes a HEAD request to see when client is ready."""
    return "ok"


@app.route('/', methods=['GET'])
def handle():
    """Crossdock sends GET requests with query params to initiate test."""
    behavior = request.args['behavior']
    server = request.args['server']
    transport = request.args['transport']

    fn = BEHAVIORS.get(behavior)

    if fn is None:
        return json.dumps([{
            "status": SKIPPED,
            "output": "Not implemented",
        }])

    try:
        resp = fn(server, transport)
        return json.dumps([{
            "status": PASSED,
            "output": resp,
        }])
    except Exception as e:
        return json.dumps([{
            "status": FAILED,
            "outout": "%s" % e
        }])


def start():
    """Start yarpc-python-sync test harness."""
    app.run(host='0.0.0.0', port=8080)
