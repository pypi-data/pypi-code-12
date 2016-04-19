#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import product

class BDProduct(product.EProduct, bd_common.BDCommon):

    @classmethod
    def wrap(cls, models, build = True, handler = None, **kwargs):
        def handler(model):
            model.update(
                name = model["short_description"],
                code = model["product_id"],
                currency = "GBP"
            )

        return super(BDProduct, cls).wrap(
            models,
            build = build,
            handler = handler,
            **kwargs
        )

    def unwrap(self, **kwargs):
        result = product.EProduct.unwrap(self, **kwargs)
        result.update(
            short_description = self.name
        )
        return result
