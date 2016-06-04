#-*- coding: UTF-8 -*-

import requests

class Api(object):
    def __init__(self, nick, passwd, root_url='http://shikimori.org/api/'):
        super(Api, self).__init__()

        self.root_url = root_url

        self.nick = nick
        self.passwd = passwd

        token_url = self.root_url + 'access_token?nickname={}&password={}'.format(self.nick, self.passwd)
        self.token = requests.get(token_url).json()['api_access_token']

        self.headers = {'X-User-Nickname': self.nick,
                        'X-User-Api-Access-Token': self.token,
                        'User-Agent': 'PyShiki'}
        self.session = requests.Session() # Session for http-requests
        self.session.headers.update(self.headers)

    def _makeReq(self, request, meth):
        args = request._method_args
        req_url = self.root_url + request._method_name
        if meth == 'get':
            r = self.session.get(req_url, params=args)
        elif meth == 'post':
            r = self.session.post(req_url, json=args)
        elif meth == 'patch':
            r = self.session.patch(req_url, json=args)
        elif meth == 'put':
            r = self.session.put(req_url, json=args)
        elif meth == 'delete':
            r = self.session.delete(req_url)
        return r.json()


    def __rerp__(self):
        return '<API-object nickname={} token={}>'.format(self.nick, self.token)

    
    def __getattr__(self, method_name):
        return Request(self, method_name)


class Request(object):

    def __init__(self, api, method_name):
        self._api = api
        self._method_name = method_name

    def __call__(self, path=None, **method_args):
        if path:
            self._method_name += '/' + str(path)
        self._method_args = method_args
        return self

    def get(self):
        return self._api._makeReq(self, 'get')

    def post(self, **args):
        return self._api._makeReq(self, 'post')

    def patch(self, **args):
        return self._api._makeReq(self, 'patch')

    def put(self, **args):
        return self._api._makeReq(self, 'put')

    def delete(self, **args):
        return self._api._makeReq(self, 'delete')

