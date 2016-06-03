# -*- coding: utf-8 -*-
__author__ = 'Thomas Eberle'

from tgbot.basicapi.model.user  import User


class MessageEntity:

    def __init__(self,type,offset,length,url=None,user:User=None):
        self.type = type
        self.offset = offset
        self.length = length
        self.url = url
        self.user = user
