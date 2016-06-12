# -*- coding: utf-8 -*-
__author__ = 'Thomas'


from abc import ABCMeta,abstractmethod

class LanguageGetterAbstract(metaclass=ABCMeta):


    def __init__(self,domain,localedir,standard):
        self.domain = domain
        self.localedir = localedir
        self.standard = standard

    @staticmethod
    @abstractmethod
    def getlanguage(user_id):
        pass