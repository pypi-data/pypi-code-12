#coding:utf-8

import os
import json
import traceback
from requests import get, post

__author__ = 'lufeng'

class Automagic(object):
    """
    无法用言语表达的一个类
    """

    def __init__(self, clientref, base):
        self.base = base
        self.clientref = clientref

    def __getattr__(self, name):
        base2 = self.base[:]
        base2.append(name)
        return Automagic(self.clientref, base2)

    def __call__(self, *args, **kargs):
        if not self.base:
            raise AttributeError("something wrong here in Automagic __call__")
        if len(self.base) < 2:
            raise AttributeError("no method called: %s" % ".".join(self.base))
        func = "/".join(self.base[0:])
        return self.clientref.call_func(func, *args, **kargs)


class BaseService(object):
    """
    cmdb客户端链接工具
    """
    def __init__(self, app, host, secretid=None, signature=None, version="v1"):
        self.app = app
        self.host = host
        self.secretid = secretid
        self.signature = signature
        self.version = version

    def get_resource(self, path, *args, **kwargs):
        code = 500
        url = "{0}/resource/{1}/{2}.json".format(self.host, self.version, path)
        try:
            headers = {
                "x-secretid": self.secretid,
                "x-signature": self.signature
            }
            if args:
                headers.update({"Content-Type": "application/json"})
            if args:
                body = json.dumps(args[0])
            else:
                body = kwargs
            res = post(url, data=body, headers=headers)
            code = res.status_code
            return res.json()
        except ValueError, error:
            if self.app:
                self.app.logger.error(res.text)
            if code == 404:
                message = "url={0} not found!".format(url)
            else:
                message = error.message
            return {"code": code, "success": False, "message": message, "data": ""}
        except Exception, error:
            if self.app:
                self.app.logger.error(traceback.format_exc())
            return {"code": code, "success": False, "message": error.message, "data": ""}

    def call_func(self, func, *args, **kwargs):
        """
        """
        return self.get_resource(func, *args, **kwargs)

    def __getattr__(self, name):
        return Automagic(self, [name])