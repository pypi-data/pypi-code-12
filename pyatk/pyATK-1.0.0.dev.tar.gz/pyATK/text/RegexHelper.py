#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re


def is_number(n):
    if is_integer(n) or is_real(n):
        return True
    return False


def is_real(n):
    if re.match("^[-+]?[0-9]*\.[0-9]+$", n):
        return True
    return False


def is_integer(n):
    """
    >>> is_integer("-9")
    True
    >>> is_integer("+982798739")
    True
    >>> is_integer("0")
    True
    >>> is_integer("1.0")
    False
    >>> is_integer("some random string")
    False
    """
    if re.match("^[-+]?[0-9]+$", n):
        return True
    return False


def is_hex(s):
    """
    >>> is_hex("0x123")
    True
    >>> is_hex("0xCAFE")
    True
    >>> is_hex("AAA")
    False
    >>> is_hex("0xGGG")
    False
    """
    if re.match("^0x[a-fA-F0-9]+$", s, re.IGNORECASE):
        return True
    return False


def is_valid_ip_address(s):
    if re.match("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", s):
        return True
    return False


def is_blank(s):
    """
    >>> is_blank("")
    True
    >>> is_blank("not so empty")
    False
    """
    if re.match("^$", s):
        return True
    return False


def is_email(s):
    """
    >>> is_email("Test-123_456@gmail.com")
    True
    >>> is_email("salut le monde")
    False
    """
    if re.match("^[a-zA-Z0-9_\.-]+@[a-zA-Z\.]+[a-zA-Z]{3}", s):
        return True
    return False
