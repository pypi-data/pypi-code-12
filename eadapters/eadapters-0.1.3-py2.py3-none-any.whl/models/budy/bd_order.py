#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import bd_common
from . import bd_address
from . import bd_bag_line

from .. import order

class BDOrder(order.EOrder, bd_common.BDCommon):

    key = appier.field()

    @classmethod
    def wrap(cls, models, build = True, handler = None, **kwargs):
        def handler(model):
            lines = model.get("lines", [])
            shipping_address = model.get("shipping_address", {})
            billing_address = model.get("billing_address", {})
            model.update(
                lines = bd_bag_line.BDBagLine.wrap(lines),
                shipping_address = bd_address.BDAddress.wrap(shipping_address) if shipping_address else None,
                billing_address = bd_address.BDAddress.wrap(billing_address) if billing_address else None
            )

        return super(BDOrder, cls).wrap(
            models,
            build = build,
            handler = handler,
            **kwargs
        )

    @classmethod
    def _ident_name(cls):
        return "key"

    @classmethod
    @bd_common.handle_error
    def _get(cls, id):
        api = cls._get_api_g()
        order = api.get_order(id)
        order = cls.wrap(order)
        return order

    @bd_common.handle_error
    def set_shipping_address_s(self, address):
        api = self._get_api()
        api.set_shipping_address_order(self.key, address)

    @bd_common.handle_error
    def set_billing_address_s(self, address):
        api = self._get_api()
        api.set_billing_address_order(self.key, address)

    @bd_common.handle_error
    def set_email_s(self, email):
        api = self._get_api()
        api.set_email_order(self.key, dict(email = email))

    @bd_common.handle_error
    def set_referral_s(self, referral):
        api = self._get_api()
        api.set_referral_order(self.key, referral)

    @bd_common.handle_error
    def set_voucher_s(self, voucher):
        api = self._get_api()
        api.set_voucher_order(self.key, voucher)

    @bd_common.handle_error
    def pay_s(self, payment_data):
        api = self._get_api()
        api.pay_order(self.key, payment_data)
