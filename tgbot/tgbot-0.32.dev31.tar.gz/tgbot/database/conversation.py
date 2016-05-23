# -*- coding: utf-8 -*-
__author__ = 'Thomas'

from abc import ABCMeta,abstractstaticmethod

class ConversationAbstract(metaclass=ABCMeta):

    @abstractstaticmethod
    def getconversation(self,user_id):
        pass

    @abstractstaticmethod
    def deleteconversation(self,user_id):
        pass

    @abstractstaticmethod
    def addtoconversation(self,user_id,question,answer):
        pass

    @abstractstaticmethod
    def getfromconversation(self,user_id,question):
        pass

    @abstractstaticmethod
    def setconversation(self,user_id,command):
        pass