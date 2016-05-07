#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011
"""
Class interface with functions required by driver implementation
"""


class BaseDriver(object):
    """Simple interface"""
    def __init__(self):
        """Class init"""
        raise NotImplementedError("__init__ not implemented")

    def init(self):
        """dummy init function"""
        raise NotImplementedError("init not implemented")

    def cmd(self, char, enable=0):
        """write command"""
        raise NotImplementedError("cmd not implemented")

    def shutdown(self):
        """shutdown procedure"""
        raise NotImplementedError("shutdown not implemented")

    def send(self, enable=0):
        """send ack command"""
        raise NotImplementedError("send not implemented")

    def write(self, char, enable=0):
        """write data to lcd"""
        raise NotImplementedError("write not implemented")

    def char(self, char, enable=0):
        """write char to lcd"""
        raise NotImplementedError("char not implemented")

    def set_mode(self, mode):
        """sets driver mode. 4/8 bit"""
        raise NotImplementedError("set_mode not implemented")
