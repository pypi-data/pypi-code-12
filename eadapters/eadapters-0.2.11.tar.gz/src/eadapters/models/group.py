#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EGroup(base.EBase):

    name = appier.field()

    order = appier.field(
        type = int
    )
