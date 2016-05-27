#!/usr/bin/python
# -*- coding: utf-8 -*-
# NoJoy_DI (c) 2016 by Andre Karlsson<andre.karlsson@protractus.se>
#
# NorseBot is licensed under a
# Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc-nd/3.0/>
#
#
# Filename: exceptions by: andrek
# Timesamp: 2016-05-18 :: 14:58

class DIException(Exception):
    """Base exception"""
    pass

class PatternizerException(DIException):

    def __init__(self, s_def, req_tokens):
        last_def = req_tokens[-1]
        super(PatternizerException, self).__init__(
             "Service %s[%s] is requesting %s[%s]. Chain: %s"
             % (last_def.name, last_def._mypattern.__name__, s_def.name, s_def._mypattern.__name__,
                " => ".join([i.name for i in req_tokens])
                )
         )