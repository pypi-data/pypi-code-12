__author__ = 'hiepsimu'
import numconv


def hex_to_base62(text):
    a = numconv.NumConv(16).str2int(text)
    return numconv.NumConv(62).int2str(a)


def base62_to_hex(text):
    a = numconv.NumConv(62).str2int(text)
    return numconv.NumConv(16).int2str(a)