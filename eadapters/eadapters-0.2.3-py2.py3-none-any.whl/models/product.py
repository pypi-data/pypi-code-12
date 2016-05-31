#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EProduct(base.EBase):

    SIZE_ALIAS = dict(
        thumbnail = ("70",),
        large = ("1000",)
    )

    GENDER_ALIAS = dict(
        Male = "Men",
        Female = "Women",
        Both = "Unisex"
    )

    name = appier.field()

    description = appier.field()

    code = appier.field()

    size = appier.field(
        type = int
    )

    scale = appier.field(
        type = int
    )

    images = appier.field(
        type = list
    )

    price = appier.field(
        type = float
    )

    @classmethod
    def _build(cls, model, map):
        super(EProduct, cls)._build(model, map)
        model["value"] = model["name"]
        for name, size in (
            ("thumbnail", 400),
            ("thumbnail_2x", 800),
            ("large", 1000),
            ("large_2x", 1000)
        ):
            name_i = name + "_image"
            model[name_i] = cls._get_image(model, size = name)
            model[name_i] = model[name_i] or cls._get_image(
                model,
                size = str(size),
                strict = False
            )

    @classmethod
    def _sizes(cls, size):
        alias = cls.SIZE_ALIAS.get(size, ())
        return [size] + list(alias)

    @classmethod
    def _get_image(cls, model, index = 1, size = "thumbnail", strict = True):
        images = cls._get_images(model, size = size)
        for image in images:
            if not image["order"] == index and strict: continue
            return image
        return None

    @classmethod
    def _get_images(cls, model, size = "thumbnail", sort = True):
        images = model.get("images", None)
        if not images: return []
        if "images" in images: images = images["images"]
        sizes = cls._sizes(size)
        _images = []
        for image in images:
            if not image or not isinstance(image, dict): continue
            if not image["size"] in sizes: continue
            _images.append(image)
        if sort: _images.sort(key = lambda item: item["order"])
        return _images

    @classmethod
    def _get_measurements(cls, model, sort = True):
        measurements = model.get("measurements", None)
        if not measurements: return []
        if sort: measurements.sort(key = lambda item: item["value"])
        return measurements

    @classmethod
    def _get_currency(cls, model):
        return "GBP"

    def get_image_url(self, size):
        image = self.images[0]
        url = image.get(size, None)
        return url

    def get_image(self, index = 1, size = "thumbnail"):
        return self.__class__.get_image(self.model, index = index, size = size)

    def get_images(self, size = "thumbnail", sort = True):
        return self.__class__._get_images(self.model, size = size, sort = sort)

    def get_measurements(self, sort = True):
        return self.__class__._get_measurements(self.model, sort = sort)

    def get_price(self, currency = "EUR", field = "totalPriceValue"):
        if hasattr(self, "price"): return self.price
        if not self.variants: return None
        variant = self.variants[0]
        prices = variant.get("prices", [])
        if not prices: return None
        for price in prices:
            _currency = price["currencyIsoCode"]
            if not _currency == currency: continue
            return price[field]
        return None

    def get_gender(self, default = "Male"):
        if hasattr(self, "gender"): gender = self.gender
        gender = gender or default
        return self.__class__.GENDER_ALIAS.get(gender, gender)
