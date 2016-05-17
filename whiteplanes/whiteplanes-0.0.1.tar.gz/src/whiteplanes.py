#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Whiteplanes is whitespace interpreter written in python.

Homepage: http://whiteplanes.github.io
Copyright (c) 2016 Takuya Katsurada.
License: MIT (see README.md for details)
"""
from context import Context
from command import Command, Register


########################################################################
# Whiteplanes
########################################################################
class Whiteplanes(object):
    def __init__(self, code):
        self.code = code
        self.commands = Whiteplanes.pause(code)

    def run(self, *, context=None):
        Context.register(type(context))
        [command(context=context) for command in self.commands if command.name == Register]

        while (context.counter < len(self.commands)):
            command = self.commands[context.counter]
            if command.name == Register:
                context.counter += 1
                continue
            command(context=context)
            context.counter += 1

    @classmethod
    def pause(cls, source):
        code = [ch for ch in source if ch in Command.characters()]
        return [command for command in Command.make(code)]
