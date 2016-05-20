#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Debugger:
    def __init__(self, is_debug):
        self.is_debug = is_debug
        self.mode = {
            "LOG": 0x0001,
            "WARN": 0x0002,
            "ERROR": 0x0004,
        }
        end = '\033[0m'
        self.BLUE = {"head": '\033[94m', "tail": end}
        self.YELLOW = {"head": '\033[93m', "tail": end}
        self.RED = {"head": '\033[91m', "tail": end}
        self.GRAY = {"head": '\033[90m', "tail": end}

    def _output(self, mode, *text):
        if (self.is_debug):
            if (mode == self.mode["LOG"]):
                type_str = "D"
                head = self.BLUE["head"]
                tail = self.BLUE["tail"]
            elif (mode == self.mode["WARN"]):
                type_str = "W"
                head = self.YELLOW["head"]
                tail = self.YELLOW["tail"]
            elif (mode == self.mode["ERROR"]):
                type_str = "E"
                head = self.RED["head"]
                tail = self.RED["tail"]
            else:
                type_str = "U"
                head = self.GRAY["head"]
                tail = self.GRAY["tail"]

            formatted = "%s[%s][%s]:" % (head, type_str, self.__class__.__name__)
            for t in text:
                formatted = "%s %s" % (formatted, t)
            print("%s%s%s" % (head, formatted, tail))

    def log(self, *text):
        self._output(self.mode["LOG"], *text)

    def warn(self, *text):
        self._output(self.mode["WARN"], *text)

    def error(self, *text):
        self._output(self.mode["ERROR"], *text)
