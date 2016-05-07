#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,W0231
"""Dummy lcd driver. Used in tests"""

from charlcd.drivers.base import BaseDriver


class Null(BaseDriver):
    """Dummy LCD driver"""
    def __init__(self):
        """empty init class"""
        self.pins = {
            'RS': 4,
            'E': 5,
            'E2': None,
            'DB4': 0,
            'DB5': 1,
            'DB6': 2,
            'DB7': 3
        }
        return

    def init(self):
        """init driver"""
        return

    def cmd(self, char, enable=0):
        """send command to lcd"""
        return char

    def shutdown(self):
        """shutdown steps"""
        return

    def send(self, enable=0):
        """send data to lcd"""
        return

    def write(self, char, enable=0):
        """write to lcd"""
        return char

    def char(self, char, enable=0):
        """send char to lcd"""
        return ord(char)

    def set_mode(self, mode):
        """set lcd mode"""
        return mode
