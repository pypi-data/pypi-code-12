#!/usr/bin/env python3
# coding: utf-8

from . import error

def check_response(res):
    if res.status_code == 200:
        return
    raise error.UnexpectedResponse(res)

def comma(data):
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return ','.join(data)

def integer(data):
    return None if data is None else int(data)
