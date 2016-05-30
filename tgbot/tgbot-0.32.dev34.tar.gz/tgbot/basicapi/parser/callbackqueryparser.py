#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Thomas'


from tgbot.tglogging import logger


def parsecallbackquery(callbackquery,args):
    logger.info(str(callbackquery))
    #get from callback_data the value of method which should be activated.
    pass
