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
        req.set_header('User-Agent', 'Python ocapi connector - Brython version 1.2')
        if data:
            if headers:
                for k, v in list(headers.items()):
                    print("Setting header {}:{}".format(k, v))
                    req.set_header(k, v)
                if 'Content-Type' not in headers:
                    req.set_header('Content-Type', 'application/x-www-form-urlencoded')
            else:
                req.set_header('Content-Type', 'application/x-www-form-urlencoded')
            if isinstance(data, list):
                data = ["{}={}".format(window.encodeURIComponent(key), window.encodeURIComponent(str(value))) for key, value in data]
                data = "&".join(data)
            req.send(data)
        else:
            req.send()

    def on_complete(self, req):
        self.data = req

    def read(self):
        return self.data.text

    def getheaders(self):
        if hasattr(self.data, "headers"):
            _list = [i.split(":", 1) for i in self.data.headers]
        else:
            var = self.data.getAllResponseHeaders()
            _list = [i.split(":", 1) for i in var.splitlines()]
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



class log(object):
    @staticmethod
    def info(msg):
        print("INFO:{}".format(msg))

    @staticmethod
    def warn(msg):
        print("WARN:{}".format(msg))

    @staticmethod
    def debug(msg):
        print("DEBUG:{}".format(msg))

    @staticmethod
    def error(msg):
        print("ERROR:{}".format(msg))
