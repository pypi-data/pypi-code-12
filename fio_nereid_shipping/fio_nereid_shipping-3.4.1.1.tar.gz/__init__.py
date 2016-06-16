# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: see LICENSE for details.
"""
from trytond.pool import Pool
from checkout import Checkout
from website import Website, WebsiteCarrier


def register():
    Pool.register(
        Checkout,
        Website,
        WebsiteCarrier,
        module='nereid_shipping', type_='model'
    )
