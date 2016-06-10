# -*- coding: utf-8 -*-
__author__ = 'Thomas Eberle'

import ast

import redis

from tgbot.config.tgbotconfigparser import TGBotConfigParser
from tgbot.tglogging import logger
import tgbot

class TGRedis:

    limitserver = redis.StrictRedis(host="localhost", port="6379", db=0)
    convserver = redis.StrictRedis(host="localhost", port="6379", db=1,decode_responses=True)
    convserver.set_response_callback("HGET",str)

    def __init__(self,limitdb=0,convdb=1):
        if limitdb == convdb:
            return
        self.limitdb = limitdb
        self.convdb = convdb
        TGRedis.limitserver = redis.StrictRedis(host="localhost", port="6379", db=limitdb)
        TGRedis.convserver = redis.StrictRedis(host="localhost", port="6379", db=convdb,decode_responses=True)
        TGRedis.convserver.set_response_callback("HGET",str)


    def addtoconv(self,message,value):
        pass

    @staticmethod
    def setconvcommand(message,value):
        user = message.from_User
        pipe = TGRedis.convserver.pipeline()
        pipe.hset(user.chat_id,"command",value)
        pipe.expire(user.chat_id,120)
        pipe.execute()

    @staticmethod
    def getconvcommand(message):
        user = message.from_User
        result = TGRedis.convserver.hget(user.chat_id,"command")
        if result:
            return str(result)
        else:
            return result

    @staticmethod
    def setconvkey(message,key,value):
        user = message.from_User
        pipe = TGRedis.convserver.pipeline()
        pipe.hset(user.chat_id,key,value)
        pipe.expire(user.chat_id,120)
        pipe.execute()

    @staticmethod
    def getconvkey(message,key):
        user = message.from_User
        return TGRedis.convserver.hget(user.chat_id,key)

    @staticmethod
    def getconv(message):
        user = message.from_User
        return str(TGRedis.convserver.get(user.chat_id))

    @staticmethod
    def deleteconv(message):
        user = message.from_User
        TGRedis.convserver.delete(user.chat_id)


    @staticmethod
    def getmessage(message):
        user = message.from_User
        return TGRedis.limitserver.get(str(user.chat_id))

    @staticmethod
    def increasemessage(message):
        expire = tgbot.iniconfig["basics"]["commandlimittime"]
        user = message.from_User
        limit_id = str(user.chat_id)+"/"+str(message.chat_id())
        pipe = TGRedis.limitserver.pipeline()
        pipe.get(limit_id)
        pipe.incr(limit_id)
        values = pipe.execute()
        if not values[0]:
            TGRedis.limitserver.expire(limit_id, expire)

        logger.debug("Response from Redis for key " + limit_id + ": " + str(values))
