#!/usr/bin/python3
# -*- coding: utf-8 -*-

UTF_8_ENCODING = "utf-8"
ISO_8895_1_ENCODING = "iso-8895-1"
WINDOWS_1252_ENCODING = "windows-1252"
MAC_ROMAN_ENCODING = "macroman"
ASCII_ENCODING = "us-ascii"

encodings = (UTF_8_ENCODING, ISO_8895_1_ENCODING, WINDOWS_1252_ENCODING, MAC_ROMAN_ENCODING, ASCII_ENCODING)


def getEncoding(filename):
    """
    >>> getEncoding(__file__)
    'utf-8'
    """
    for encoding in encodings:
        try:
            file = open(filename, 'rb')
            payload = file.read()
            payload.decode(encoding)
            return encoding

        except FileNotFoundError:
            raise FileNotFoundError("file " + filename + " is not found.")
        except:
            if encoding == encodings[-1]:
                return None
            continue


def getDataEncoding(payload):
    """
    >>> f = open(__file__)
    >>> getDataEncoding(f.readlines())
    'us-ascii'
    """
    for encoding in encodings:
        try:
            payload.decode(encoding)
            return encoding
        except:
            if encoding == encodings[-1]:
                return ASCII_ENCODING
            continue


def isAscii(filename):
    """
    >>> isAscii(__file__)
    True
    """
    try:
        data = open(filename, 'r').read()
        data.encode().decode('ASCII')
    except UnicodeDecodeError:
        return False
    else:
        return True


def isUtf8(filename):
    """
    >>> isUtf8(__file__)
    True
    """
    try:
        data = open(filename, 'r').read()
        data.encode().decode('UTF-8')
    except UnicodeDecodeError:
        return False
    else:
        return True


