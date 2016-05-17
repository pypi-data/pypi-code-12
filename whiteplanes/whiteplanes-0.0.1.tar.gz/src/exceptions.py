#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
# Exception
########################################################################

# All brainfuck exceptions should also be derived from this class.
class Error(Exception):
    pass

# Raised when the parser encounters a syntax error.
class SyntaxError(Error):
    pass
