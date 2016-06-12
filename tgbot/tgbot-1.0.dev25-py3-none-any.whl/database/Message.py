# -*- coding: utf-8 -*-
__author__ = 'Thomas'

from abc import ABCMeta,abstractmethod

class ConversationAbstract(metaclass=ABCMeta):

    @abstractmethod
    def getconversation(self,user_id):
        pass

    @abstractmethod
    def deleteconversation(self,user_id):
        pass

    @abstractmethod
    def addtoconversation(self,user_id,question,answer):
        pass

    @abstractmethod
    def getfromconversation(self,user_id,question):
        pass

    @abstractmethod
    def setconversation(self,user_id,command):
        pass