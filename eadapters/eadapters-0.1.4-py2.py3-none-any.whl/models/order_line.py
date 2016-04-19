#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EOrderLine(base.EBase):

    quantity = appier.field(
        type = float
    )

    total = appier.field(
        type = float
    )

    size = appier.field(
        type = int
    )

    scale = appier.field(
        type = int
    )

    meta = appier.field(
        type = dict
    )

    meta_j = appier.field()

    product = appier.field(
        type = appier.reference(
            "EProduct",
            name = "id"
        )
    )

    @classmethod
    def _build(cls, model, map):
        super(EOrderLine, cls)._build(model, map)

        meta = model.get("meta", {}) or {}
        image_url = meta.get("image_url", None)
        if not image_url: return

        product = model["product"]
        thumbnail = product["thumbnail"] or {}
        large_image = product["large_image"] or {}
        thumbnail["url"] = image_url
        large_image["url"] = image_url
        product["thumbnail"] = thumbnail
        product["large_image"] = large_image
