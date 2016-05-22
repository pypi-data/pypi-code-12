# -*- coding: utf-8 -*-
__author__ = 'Thomas Eberle'

from tgbot.tglogging import *
from tgbot.basicapi.model.base import Base


class User(Base):
    def getchatid(self):
        return self.id

    def __createfromdata__(self, data):
        self.id = data["id"]
        try:
            self.first_name = data["first_name"]
        except KeyError:
            self.first_name = ""
            logger.debug("No first name available.")
        try:
            self.last_name = ""
            self.last_name = data["last_name"]
        except KeyError:
            logger.debug("No last name available.")
        try:
            self.username = data["username"]
        except KeyError:
            self.username = ""
            logger.debug("No username available.")

    def __init__(self, data=None, id=None, first_name=None, last_name=None, username=None):
        if data:
            self.__createfromdata__(data)
        else:
            self.id = id
            self.first_name = first_name
            self.last_name = last_name
            self.username = username
