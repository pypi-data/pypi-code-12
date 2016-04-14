#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913,R0902
"""Interface for buffered inputs
Provide functions that must be implemented by and buffered lcd
"""


class Buffered(object):
    """Required functions for buffered lcd driver"""
    def init(self):
        """screen and buffer init"""
        raise NotImplementedError("init not implemented")

    def buffer_clear(self, from_x=None, from_y=None, width=None, height=None):
        """clears buffer"""
        raise NotImplementedError("buffer_clear not implemented")

    def flush(self):
        """Flush buffer to screen, skips chars that didn't change"""
        raise NotImplementedError("flush not implemented")
