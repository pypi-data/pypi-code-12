# coding:utf-8

import os
import json
import traceback
from loader import load_services

__author__ = 'lufeng'


class Service(object):
    """
    cmdb客户端链接工具
    """

    def __init__(self, name, app=None, host=None, secretid=None, signature=None):
        self.name = name
        self.app = app
        self.host = host
        self._serv = None
        self.secretid = secretid
        self.signature = signature

    def init_app(self, app):
        """
        初始化cmdb客户端
        """
        self.app = app
        self.host = self.app.config.get("{0}_API_URL".format(self.name.upper()))
        self.secretid = self.app.config.get("{0}_SECRET_ID".format(self.name.upper()))
        self.signature = self.app.config.get("{0}_SIGNATURE".format(self.name.upper()))
        self.version = self.app.config.get("{0}_API_VERSION".format(self.name.upper()), "v1")
        if not all([self.host, self.secretid, self.signature]):
            raise Exception(u"all {0}_URL, {0}_SECRET_ID, {0}_SIGNATURE is required".format(self.name.upper()))
        serv = load_services(self.app, self.name)
        self._serv = serv(self.app, self.host, self.secretid, self.signature, self.version)

    def __getattr__(self, item):
        if self._serv:
            return getattr(self._serv, item)
        raise Exception("service for %s not found!".format(self.name))

