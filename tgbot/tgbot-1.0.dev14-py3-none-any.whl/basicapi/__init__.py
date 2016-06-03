# -*- coding: utf-8 -*-
__author__ = 'Thomas'


from tgbot.basicapi.model.message import Message
from tgbot.basicapi.model.inlineQuery import InlineQuery
from tgbot.basicapi.model.callbackQuery import CallBackQuery
from tgbot.tglogging import logger
from tgbot.basicapi.parser import parsemessage,parseinline,parsecallbackquery
import tgbot
import gettext
from tgbot.database.language import LanguageGetterAbstract


def activatebot(data,wartungsmodus,commands,conversationmethods,callbackclasses,inlinecommands,conversation):

    logger.debug("Message arrived.\nMessage: " + str(data))
    if "message" in data:
        message = Message(data=data["message"])
        #tgbot.mainmessage = message
        parsemessage(message,commands,conversationmethods,wartungsmodus,conversation)
    elif "callback_query" in data:
        callback = CallBackQuery(data=data["callback_query"])
        parsecallbackquery(callback,callbackclasses)
    elif "inline_query" in data:
        inline = InlineQuery(data=data["inline_query"])
        parseinline(inline,inlinecommands)
        logger.debug("IN INLINE QUERY")

