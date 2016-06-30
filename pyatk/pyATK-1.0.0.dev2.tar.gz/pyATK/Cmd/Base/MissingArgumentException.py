# -*- coding: utf-8 -*-


class MissingArgumentException(Exception):
    def __init__(self, arg):
        self.argument = arg

    def __str__(self):
        return "Missing value for \"" + self.argument + "\""
