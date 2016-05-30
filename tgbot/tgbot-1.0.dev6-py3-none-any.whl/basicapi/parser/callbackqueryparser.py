#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Thomas'

import ast
from tgbot.tglogging import logger
from tgbot.basicapi.parser.methodparser import parsemethods


def parsecallbackquery(callbackquery,args):
    logger.info("CALLBACK DATA: "+str(callbackquery.data))
    data = ast.literal_eval(callbackquery.data)
    method = data["method"]
    parsemethods(callbackquery,method,args)
