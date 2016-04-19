#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import order_line

class BDOrderLine(order_line.EOrderLine, bd_common.BDCommon):
    pass
