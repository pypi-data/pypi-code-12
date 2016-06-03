# -*- coding: utf-8 -*-
__author__ = 'Thomas'

import inspect
from tgbot.tglogging import logger
from tgbot.basicapi.parser.methodparser import parsemethods


def parseinline(inline,args):
    query = inline.query
    parsemethods(inline,query,args)