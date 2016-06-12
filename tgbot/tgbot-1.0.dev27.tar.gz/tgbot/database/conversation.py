# -*- coding: utf-8 -*-
__author__ = 'Thomas'

from abc import ABCMeta,abstractmethod

class ConversationAbstract(metaclass=ABCMeta):


    @staticmethod
    @abstractmethod
    def getconversation(user_id):
        pass


    @staticmethod
    @abstractmethod
    def getconversationcommand(user_id):
        pass

    @staticmethod
    @abstractmethod
    def deleteconversation(user_id):
        pass

    @staticmethod
    @abstractmethod
    def addtoconversation(user_id, key, value):
        pass

    @staticmethod
    @abstractmethod
    def getconversationvalue(user_id,command):
        pass

    @staticmethod
    @abstractmethod
    def getfromconversation(user_id,question):
        pass

    @staticmethod
    @abstractmethod
    def setconversation(user_id,command,value=None):
        pass