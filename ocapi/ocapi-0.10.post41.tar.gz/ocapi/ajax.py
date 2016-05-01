#!/usr/bin/env python
# -*- coding:utf-8 -*-
# (c)Ing. Zdenek Dlauhy, Michal Dlauhý, info@dlauhy.cz

import sys
if sys.platform == "brython":
    from browser import ajax, window

class Connection(object):
    def __init__(self, url="/login", port=443, data=None, method="POST",
            headers=None, debug=None, cookie=None, tls=True, timeout=4, host="pripravto.cz"):
        self.data = None
        req = ajax.ajax()
        req.bind('complete', self.on_complete)
        req.set_timeout(timeout, self.err_msg)
        req.open(method, url, False)
        if data:
            req.set_header('content-type', 'application/x-www-form-urlencoded')
            if isinstance(data, list):
                data = ["{}={}".format(window.encodeURIComponent(key), window.encodeURIComponent(value)) for key, value in data]
                data = "&".join(data)
            req.send(data)
        else:
            req.send()

    def on_complete(self, req):
        self.data = req

    def read(self):
        return self.data.text

    def getheaders(self):
        _list = [i.split(":", 1) for i in self.data.headers]
        data = {}
        for line in _list:
            if line:
                if line[0]:
                    key, value = line
                    key = key.strip()
                    value = value.strip()
                    data[key] = value
        return data

    @property
    def status(self):
        return self.data.status

    @property
    def reason(self):
        return self.data.status

    def err_msg(self):
        print("error")
