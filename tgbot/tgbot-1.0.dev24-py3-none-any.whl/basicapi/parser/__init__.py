# -*- coding: utf-8 -*-
__author__ = 'Thomas'

import re

from tgbot.basicapi.commands import sendreply
from tgbot.basicapi.parser import commandparser
from tgbot.basicapi.parser import textparser,inlineparser,callbackqueryparser
from tgbot.resources import emoji
from tgbot.database.conversation import ConversationAbstract
from tgbot.tgredis import *
import tgbot
regex = re.compile(r'/(?P<command>\w+)(\s(?P<parameter>.+))?')

def isadmin(message):
        user = message.from_User
        if str(user.chat_id) in tgbot.iniconfig.get("basics", "superadmins"):
            logger.debug("@" + user.username + "(" + str(user.chat_id) + ") ist ein SuperAdmin.")
            return True
        else:
            logger.debug("@" + user.username + "(" + str(user.chat_id) + ") ist kein SuperAdmin")
            return False

def parsemessage(message, botcommands,conversationmethods, wartungsmodus, conversation:ConversationAbstract):
    user = message.from_User
    # parsereplycommand(message)
    if message.text is not None:
        #WARTUNGSMODUS
        if wartungsmodus and not isadmin(message):
            sendreply(message, message.chat_id(), emoji.warning + "ICH WERDE GERADE GEWARTET!")
            return
        #WARTUNGSMODUS ENDE
        if re.match(r'/(\w)+', message.text):
                commandparser.parsecommand(message, botcommands)
        elif conversation.getconversationmethodanddelete(user.getchatid()):
                commandparser.parseconversation(message, conversationmethods, conversation)
        elif TGRedis.getconvcommand(message):
                commandparser.parsecommand(message, botcommands)
        elif conversation and conversation.getconversationmethod(user.getchatid()):
                commandparser.parsecommand(message, botcommands)
        else:
            textparser.parsetext(message)


def parseinline(inline,args):
    # parsereplycommand(message)
    if inline.query is not None:
            inlineparser.parseinline(inline,args)

def parsecallbackquery(callbackquery,args):
    if callbackquery.callback_data is not None:
        callbackqueryparser.parsecallbackquery(callbackquery,args)



