#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import datetime

from . import base

class EOrder(base.EBase):

    status = appier.field()

    date = appier.field(
        type = int
    )

    currency = appier.field()

    sub_total = appier.field(
        type = float
    )

    discount = appier.field(
        type = float
    )

    shipping_cost = appier.field(
        type = float
    )

    total = appier.field(
        type = float
    )

    email = appier.field()

    shipping_address = appier.field(
        type = appier.reference(
            "EAddress",
            name = "id"
        )
    )

    billing_address = appier.field(
        type = appier.reference(
            "EAddress",
            name = "id"
        )
    )

    lines = appier.field(
        type = appier.references(
            "EOrderLine",
            name = "id"
        )
    )

    @property
    def quantity(self):
        return len(self.lines)

    @property
    def date_s(self):
        return self.get_date_s()

    def get_date_s(self, format = "%Y-%m-%d"):
        if not hasattr(self, "date"): return None
        if not self.date: return None
        date = datetime.datetime.utcfromtimestamp(self.date)
        return date.strftime(format)

    def is_finalized(self):
        return True
