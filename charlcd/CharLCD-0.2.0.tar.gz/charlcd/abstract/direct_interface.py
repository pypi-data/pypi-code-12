#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913,R0902

"""Interface for direct inputs
Provide functions that must be implemented by and direct lcd
"""


class Direct(object):
    """Required functions for direct lcd driver"""
    def stream(self, string):
        """Stream string - use stream_char
        Args:
            string: string to display
        """
        raise NotImplementedError("stream_string not implemented")
