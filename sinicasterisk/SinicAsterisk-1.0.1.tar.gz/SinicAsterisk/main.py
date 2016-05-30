#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015 HQM <qiminis0801@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import re


class SinicAsterisk(object):
    def __init__(self):
        pass

    def phone(self, message):
        length = len(message or '')
        if length == 11:
            message = re.sub(r'(\d{3})(\d{4})(\d{4})', r'\1****\3', message)
        return message

    def identity_card(self, message):
        length = len(message or '')
        if length == 18:
            message = re.sub(r'(\d{10})(\d{4})(\d{3}(\d|X|x))', r'\1****\3', message)
        elif length == 15:
            message = re.sub(r'(\d{8})(\d{4})(\d{3})', r'\1****\3', message)
        return message


_global_instance = SinicAsterisk()
phone = _global_instance.phone
identity_card = _global_instance.identity_card
