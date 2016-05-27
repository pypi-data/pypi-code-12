# -*- coding: utf-8 -*-
# Module for closedown API. It include base functionality of the
# RESTful web service request and parse json result. It uses Linkhub module
# to accomplish authentication APIs.
#
# Author : Kim Seongjun (pallet027@gmail.com)
# Written : 2015-06-15
# Thanks for your interest.
from io import BytesIO
import datetime
import json
from json import JSONEncoder
from urllib import quote
from collections import namedtuple

try:
    import http.client as httpclient
except ImportError:
    import httplib as httpclient
import mimetypes
from time import time as stime

import linkhub
from linkhub import LinkhubException

ServiceID = 'CLOSEDOWN';
ServiceURL = 'closedown.linkhub.co.kr';
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

class CloseDown(__with_metaclass(Singleton,object)):
    def __init__(self,LinkID,SecretKey,TimeOut = 15):
        """ 생성자.
            args
                LinkID : 링크허브에서 발급받은 LinkID
                SecretKey : 링크허브에서 발급받은 SecretKey
        """
        self.__linkID = LinkID
        self.__secretKey = SecretKey
        self.__scopes = ["170"]
        self.__tokenCache = None
        self.__conn = None
        self.__connectedAt = stime()
        self.__timeOut = TimeOut

    def _getConn(self):

        if stime() - self.__connectedAt >= self.__timeOut or self.__conn == None:
            self.__conn = httpclient.HTTPSConnection(ServiceURL)
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
                raise CloseDownException(LE.code,LE.message)

        return token

    def _httpget(self,url,CorpNum = None,UserID = None):

        headers = {"x-api-version" : APIVersion}
        headers["Authorization"] = "Bearer " + self._getToken().session_token

        conn = self._getConn()

        conn.request('GET',url,'',headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise CloseDownException(int(err.code),err.message)
        else:
            return Utils.json2obj(responseString)

    def _httppost(self,url,postData):

        headers = {"x-api-version" : APIVersion, "Content-Type" : "Application/json"}
        headers["Authorization"] = "Bearer " + self._getToken().session_token

        conn = self._getConn()

        conn.request('POST',url,postData,headers)

        response = conn.getresponse()
        responseString = response.read()

        if response.status != 200 :
            err = Utils.json2obj(responseString)
            raise CloseDownException(int(err.code),err.message)
        else:
            return Utils.json2obj(responseString)

    def getBalance(self):
        """ 잔여포인트 확인
            return
                잔여포인트 by float
            raise
                CloseDownException
        """
        try:
            return linkhub.getPartnerBalance(self._getToken())
        except LinkhubException as LE:
                raise CloseDownException(LE.code,LE.message)

    def getUnitCost(self):
        """ 주소검색 단가 확인
            return
                전송 단가 by float
            raise
                CloseDownException
        """

        result = self._httpget('/UnitCost')
        return int(result.unitCost)

    def checkCorpNum(self, CorpNum):
        """ 휴폐업 상태 조회
            args
                CorpNum : 확인하고자 하는 사업자번호
            return
                corpstate : 휴폐업상태 정보.
                    .corpNum : 사업자번호
                    .type : 사업자 유형
                        [null : 알수없음,
                         1 : 부가가치세 일반과세자,
                         2 : 부가가치세 면세과세자,
                         3 : 부가가치세 간이과세자,
                         4 : 비영리법인 또는 국가기관,
                         고유번호가 부여된 단체]
                    .state : 사업장 상태
                        [null : 알수없음
                         0 : 등록되지 않은 사업자번호
                         1 : 사업중
                         2 : 폐업
                         3 : 휴업]
                    .stateDate : 휴폐업시, 휴폐업 일자
                    .checkDate : 최종 국세청 확인 일자
            raise
                CloseDownException
        """
        try:

            url = "/Check?CN=" + CorpNum;

            return self._httpget(url)

        except LinkhubException as LE:
            raise CloseDownException(LE.code,LE.message)

    def checkCorpNums(self, CorpNumList):
        """ 휴폐업 상태 조회
            args
                CorpNumList : 확인하고자 하는 사업자번호 목록
            return
                corpstate[] : 휴폐업상태 정보의 배열
                    .corpNum : 사업자번호
                    .type : 사업자 유형
                        [null : 알수없음,
                         1 : 부가가치세 일반과세자,
                         2 : 부가가치세 면세과세자,
                         3 : 부가가치세 간이과세자,
                         4 : 비영리법인 또는 국가기관,
                         고유번호가 부여된 단체]
                    .state : 사업장 상태
                        [null : 알수없음
                         0 : 등록되지 않은 사업자번호
                         1 : 사업중
                         2 : 폐업
                         3 : 휴업]
                    .stateDate : 휴폐업시, 휴폐업 일자
                    .checkDate : 최종 국세청 확인 일자
            raise
                CloseDownException
        """
        try:

            url = "/Check";

            postData = self._stringtify(CorpNumList)

            return self._httppost(url,postData)

        except LinkhubException as LE:
            raise CloseDownException(LE.code,LE.message)

    def _stringtify(self,obj):
        return json.dumps(obj,cls=CloseDownEncoder)

class CloseDownException(Exception):
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

class CloseDownEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Utils:
    @staticmethod
    def _json_object_hook(d): return JsonObject(namedtuple('JsonObject', d.keys())(*d.values()))

    @staticmethod
    def json2obj(data):
        if (type(data) is bytes): data = data.decode()
        return json.loads(data, object_hook = Utils._json_object_hook)
