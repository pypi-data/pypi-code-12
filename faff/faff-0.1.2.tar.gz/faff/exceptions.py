#!/usr/bin/env python


class FaffException(Exception):
    pass


class InvalidInputFileException(FaffException):
    pass


class UnknownTargetRuleException(FaffException):
    pass


# TODO: Better exceptions.


class InvalidTargetException(FaffException):
    pass
