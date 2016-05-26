import sys
import json
import unittest
from woodstove import app
from bottle import tob, request
if sys.version_info >= (3, 0, 0):
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO

class _TestApp(object):
    wsapp = app.App('/')

    @wsapp.get('/')
    def get(self):
        return {"foo": "bar"}

    @wsapp.post('/')
    def post(self):
        return {"foo": "bar"}


class TestApp(unittest.TestCase):
    def test_get(self):
        ret = _TestApp().get()
        self.assertDictEqual(ret, {"data": ({"foo":"bar"},), "total": 1})
    
    def test_post(self):
        body = {"hello": "world"}
        json_body = json.dumps(body)
        request.environ['CONTENT_LENGTH'] = int(len(tob(json_body)))
        request.environ['wsgi.input'] = BytesIO()
        request.environ['wsgi.input'].write(tob(json_body))
        request.environ['wsgi.input'].seek(0)
        ret = _TestApp().post()
        self.assertDictEqual(ret, {"data": ({"foo":"bar"},), "total": 1})
