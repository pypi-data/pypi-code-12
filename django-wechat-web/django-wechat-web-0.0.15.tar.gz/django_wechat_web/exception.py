#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : wechat/exception.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年04月21日 星期四 10时31分56秒
# *************************************************

class Error(Exception):
    '''
        Error Code + Message
    '''
    def __init__(self, code, message):
        self._code = code
        self._message = message


    @property
    def errors(self):
        return {
            'errcode': self._code, 
            'errmsg': self._message
        }

    @property
    def solve(self):
        return {
            'errcode': self._code, 
            'errmsg': self._message
        }

