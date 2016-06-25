#!/usr/bin/env python
# TODO: Better exceptions.


class FaffError(Exception):
    pass


class InvalidInputFileError(FaffError):
    pass


class UnknownTargetRuleError(FaffError):
    pass


class InvalidTargetError(FaffError):
    pass
