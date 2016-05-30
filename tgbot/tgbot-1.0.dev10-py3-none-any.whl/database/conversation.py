# -*- coding: utf-8 -*-
__author__ = 'Thomas'

from abc import ABCMeta,abstractmethod

class ConversationAbstract(metaclass=ABCMeta):


    @staticmethod
    @abstractmethod
    def getconversationmethod(user_id):
        pass

    @staticmethod
    @abstractmethod
    def getconversationmethodanddelete(user_id):
        pass

    @staticmethod
    @abstractmethod
    def deleteconversation(user_id):
        pass

    @staticmethod
    @abstractmethod
    def addtoconversation(user_id,question,answer):
        pass

    @staticmethod
    @abstractmethod
    def getfromconversation(user_id,question):
        pass

    @staticmethod
    @abstractmethod
    def setconversation(user_id,command):
        pass