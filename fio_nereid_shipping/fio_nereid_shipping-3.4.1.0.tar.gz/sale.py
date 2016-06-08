# -*- coding: utf-8 -*-
"""
    sale

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: see LICENSE for details.
"""
from trytond.pool import PoolMeta

__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    def apply_shipping(self):
        """
        Apply shipping for sale
        """
        if self.carrier:
            getattr(
                self, 'apply_%s_shipping' % self.carrier.carrier_cost_method
            )()
