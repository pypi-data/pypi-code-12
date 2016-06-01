# -*- coding: utf-8 -*-
# Module for Jusolink Base API. It include base functionality of the
# RESTful web service request and parse json result. It uses Linkhub module
# to accomplish authentication APIs.
#
# http://www.jusolink.com
# Author : Jeong yohan (yhjeong@linkhub.co.kr)
# Written : 2015-05-12
# Updated : 2016-05-31
# Thanks for your interest.
from io import BytesIO
import datetime
import json
from json import JSONEncoder
from urllib import quote
from collections import namedtuple
from time import time as stime
try:
    import http.client as httpclient
except ImportError:
    import httplib as httpclient
import mimetypes

import linkhub
from linkhub import LinkhubException

ServiceID = 'JUSOLINK';
ServiceURL = 'juso.linkhub.co.kr';
APIVersion = '1.0';

def __with_metaclass(meta, *bases):
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Jusolink(__with_metaclass(Singleton,object)):
    def __init__(self,LinkID,SecretKey,timeOut=15):
        """ 생성자.
            args
                LinkID : 링크허브에서 발급받은 LinkID
                SecretKey : 링크허브에서 발급받은 SecretKey
        """
        self.__linkID = LinkID
        self.__secretKey = SecretKey
        self.__scopes = ["200"]
        self.__tokenCache = None
        self.__conn = None
        self.__connectedAt = stime()
        self.__timeOut = timeOut

    def _getConn(self):
        if stime() - self.__connectedAt >= self.__timeOut or self.__conn == None:
            self.__conn = httpclient.HTTPSConnection(ServiceURL);
            self.__connectedAt = stime()
            return self.__conn
        else:
            return self.__conn

    def _getToken(self):

        try:
            token = self.__tokenCache
        except KeyError :
            token = None

        refreshToken = True

        if token != None :
            refreshToken = token.expiration[:-5] < linkhub.getTime()

        if refreshToken :
            try:
                token = linkhub.generateToken(self.__linkID,self.__secretKey, ServiceID, None, self.__scopes)

                self.__tokenCache = token

            except LinkhubException as LE:
                raise JusolinkException(LE.code,LE.message)

        return token

    def _httpget(self,url,CorpNum = None,UserID = None):

        conn = self._getConn()

        headers = {"x-api-version" : APIVersion}
        headers["Authorization"] = "Bearer " + self._getToken().session_token

        conn.request('GET',url,'',headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise JusolinkException(int(err.code),err.message)
        else:
            return Utils.json2obj(responseString)

    def getBalance(self):
        """ 잔여포인트 확인
            return
                잔여포인트 by float
            raise
                JusolinkException
        """
        try:
            return linkhub.getPartnerBalance(self._getToken())
        except LinkhubException as LE:
                raise JusolinkException(LE.code,LE.message)

    def getUnitCost(self):
        """ 주소검색 단가 확인
            return
                전송 단가 by float
            raise
                JusolinkException
        """

        result = self._httpget('/Search/UnitCost')
        return int(result.unitCost)

    def search(self, Index, PageNum, PerPage = None, noSuggest = None, noDiff = None):
        try:

            if PageNum != None and PageNum < 1 :
                PageNum = None

            if PerPage != None :
                if PerPage < 0 :
                    PerPage = 20

            url = "/Search?Searches="

            if Index == None and Index == "" :
                raise JusolinkException(-99999999,"검색어가 입력되지 않았습니다.")

            url += quote(Index)

            url += "&PageNum=" + str(PageNum)

            if PerPage != None and PerPage > 0 :
                url += "&PerPage=" + str(PerPage)

            if noSuggest != None and noSuggest :
                url += "&noSuggest=true"

            if noDiff != None and noDiff :
                url += "&noDifferential=true"

            return self._httpget(url)

        except LinkhubException as LE:
            raise JusolinkException(LE.code,LE.message)


class JusolinkException(Exception):
    def __init__(self,code,message):
        self.code = code
        self.message = message

class JsonObject(object):
    def __init__(self,dic):
        try:
            d = dic.__dict__
        except AttributeError :
            d = dic._asdict()

        self.__dict__.update(d)

    def __getattr__(self,name):
        return None


class SearchResult(object):
    def __init__(self,**kwargs):
        self.__dict__ = kwargs


class JusoInfo(object):
    def __init__(self,**kwargs):
        self.__dict__ = kwargs

class JusolinkEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Utils:
    @staticmethod
    def _json_object_hook(d): return JsonObject(namedtuple('JsonObject', d.keys())(*d.values()))

    @staticmethod
    def json2obj(data):
        if(type(data) is bytes): data = data.decode()
        return json.loads(data, object_hook=Utils._json_object_hook)
