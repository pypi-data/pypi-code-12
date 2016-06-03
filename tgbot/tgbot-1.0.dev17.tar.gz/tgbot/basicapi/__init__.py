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


def activatebot(data,wartungsmodus,commands,conversationmethods,callbackclasses,inlinecommands,conversation,language):

    logger.debug("Message arrived.\nMessage: " + str(data))
    if "message" in data:
        message = Message(data=data["message"])
        installlanguage(message.from_User.getchatid(),language=language)
        #tgbot.mainmessage = message
        parsemessage(message,commands,conversationmethods,wartungsmodus,conversation)
    elif "callback_query" in data:
        callback = CallBackQuery(data=data["callback_query"])
        installlanguage(callback.from_User.getchatid(),language=language)
        parsecallbackquery(callback,callbackclasses)
    elif "inline_query" in data:
        inline = InlineQuery(data=data["inline_query"])
        installlanguage(inline.from_User.getchatid(),language=language)
        parseinline(inline,inlinecommands)
        logger.debug("IN INLINE QUERY")

def installlanguage(user_id,language:LanguageGetterAbstract=None):
    if not language.getlanguage(user_id):
        inter = gettext.translation(domain=language.domain,localedir=language.localedir,languages=[language.standard])
    else:
        inter = gettext.translation(domain=language.domain,localedir=language.localedir,languages=[language.getlanguage(user_id)])
    inter.install()

