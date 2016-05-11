#!/usr/bin/env python
"""
A very simple example script showing how to forge a signed HTTP
request using a token.

You may test this by creating and starting an instance ot this
signedrequest cube (which is useless besides from this testing
purpose), add a 'toto' CWUser, and create Token using this 'toto' user
credentials (in the web UI).

You may then use this token to make HTTP requests as the 'toto' user:

python misc/sreq_example.py "http://perseus:8080/view?rql=rql%3ACWUser+X&vid=ejsonexport" mytoken3 2cc4e3a337b948139668c1f81bfc3cc49969dd5971cf4f2fb509a046e1dea244ccbb77fe8ab44fdcaf8d50d53731735c558b21b97133425088f13186fe76ae1e
[{u'__cwetype__': u'CWUser',
  u'creation_date': u'2013/07/29 15:51:34',
  u'cwuri': u'None6',
  u'eid': 6,
  u'firstname': None,
  u'last_login_time': u'2013/07/29 17:09:49',
  u'login': u'admin',
  u'modification_date': u'2013/07/29 17:09:49',
  u'surname': None,
  u'upassword': None},
 {u'__cwetype__': u'CWUser',
  u'creation_date': u'2013/07/29 15:55:23',
  u'cwuri': u'http://perseus:8080/736',
  u'eid': 736,
  u'firstname': u'Toto',
  u'last_login_time': u'2013/07/29 17:14:36',
  u'login': u'toto',
  u'modification_date': u'2013/07/29 17:14:36',
  u'surname': u'Toto',
  u'upassword': None}]

"""
import hmac
import hashlib
import requests
import requests.auth
from email.utils import formatdate

def sign(req, token):
    headers_to_sign = ('Content-MD5', 'Content-Type', 'Date')
    to_sign = (req.method + req.url +
               ''.join(req.headers.get(field, '') for field in headers_to_sign))
    return hmac.new(token, to_sign).hexdigest()

def md5(data):
    h = hashlib.md5(data)
    return h.hexdigest()

class SignedRequestAuth(requests.auth.AuthBase):
    def __init__(self, token_id, secret):
        self.token_id = token_id
        self.secret = secret

    def __call__(self, r):
        if r.method in ('PUT', 'POST'):
            r.headers['Content-MD5'] = md5(r.body or '')
        r.headers['Authorization'] = 'Cubicweb %s:%s' % (self.token_id, sign(r, self.secret))
        return r

def get(url, token_id, token):
    auth = SignedRequestAuth(token_id, token)
    resp = requests.get(url,
            headers={'Accept': 'text/plain',
                     'Date': formatdate(usegmt=True)},
            auth=auth)
    return resp.json()

def post(url, token_id, token, data=None, files=None, **params):
    auth = SignedRequestAuth(token_id, token)
    _cw_fields = params.keys()
    if files:
        _cw_fields += files.keys()
    resp = requests.post(url,files=files, data=data, params=params,
            headers={'Accept': 'text/plain',
                     'Date': formatdate(usegmt=True)},
            auth=auth)
    return resp.json()

def main():
    import sys, pprint
    if len(sys.argv) != 4:
        print "3 arguments expected: url token_id and token"
        sys.exit(1)
    url, token_id, token = sys.argv[1:]

    pprint.pprint(get(url, token_id, token))

if __name__ == "__main__":
    main()
