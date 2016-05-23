# -*- coding: utf-8 -*-
"""
    koalaecommerce.baseinventory.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Base implementations of inventory items. These are in a separate module so as to avoid cyclic import errors.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

from satchless.item import Item, StockedItem


# Base Item
def compile_item_modifiers(item, item_modifiers, **kwargs):
    discounts = None
    minimum_fees = None
    surcharges = None
    tax = None

    if item_modifiers.discounts:
        calculated_discounts = []
        for discount in item_modifiers.discounts:
            if discount.applicable(item, **kwargs):
                calculated_discounts.append(discount)
        if calculated_discounts:
            discounts = max(calculated_discounts)

    if item_modifiers.minimum_fees:
        calculated_minimum_fees = []
        for minimum_fee in item_modifiers.minimum_fees:
            if minimum_fee.applicable(item, **kwargs):
                calculated_minimum_fees.append(minimum_fee)
        if calculated_minimum_fees:
            minimum_fees = max(calculated_minimum_fees)

    if item_modifiers.surcharges:
        for surcharge in item_modifiers.surcharges:
            if surcharge.applicable(item, **kwargs):
                if not surcharges:
                    surcharges = surcharge
                else:
                    surcharges += surcharge

    if item_modifiers.tax:
        tax = item_modifiers.tax

    return discounts, minimum_fees, surcharges, tax


class CustomisableItem(Item):
    _price_per_item_cache = None

    def __init__(self, sku, title, price):
        self.sku = sku
        self.title = title
        self.price = price

    def decode_sku(self):
        product_type = None
        year = None
        category = None
        special = None
        return product_type, year, category, special

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def get_price_per_item(self, item_modifiers=None, **kwargs):
        # if self._price_per_item_cache:
        #     return self._price_per_item_cache

        if not self.price:
            raise AttributeError('Item was initialised without a valid price.')

        price = self.price

        if item_modifiers:
            # Pass modifiers to function which checks if they apply to this product. yield discounts, surcharges, tax
            # Modifiers in a namedtuple?
            discount, minimum_fee, surcharge, tax = compile_item_modifiers(self, item_modifiers, **kwargs)
            if discount:
                price += discount

            if minimum_fee:
                price += minimum_fee

            if surcharge:
                price += surcharge

            if tax:
                price += tax

        # self._price_per_item_cache = price

        return price


class CustomisableStockedItem(StockedItem):
    _price_per_item_cache = None

    def __init__(self, sku, title, price):
        self.sku = sku
        self.title = title
        self.price = price

    def decode_sku(self):
        product_type = None
        year = None
        category = None
        special = None
        return product_type, year, category, special

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def get_price_per_item(self, item_modifiers=None, **kwargs):
        # if self._price_per_item_cache:
        #     return self._price_per_item_cache

        if not self.price:
            raise AttributeError('Item was initialised without a valid price.')

        price = self.price

        if item_modifiers:
            # Pass modifiers to function which checks if they apply to this product. yield discounts, surcharges, tax
            # Modifiers in a namedtuple?
            discount, minimum_fee, surcharge, tax = compile_item_modifiers(self, item_modifiers, **kwargs)
            if discount:
                price += discount

            if minimum_fee:
                price += minimum_fee

            if surcharge:
                price += surcharge

            if tax:
                price += tax

        # self._price_per_item_cache = price

        return price


class ItemNotFound(Exception):
    pass


class BaseInventoryManager(object):
    @classmethod
    def get_inventory_item(cls, sku, customization_options=None, **kwargs):
        fetched_item = cls.fetch_item(sku=sku, **kwargs)
        if customization_options:
            return fetched_item, cls.customize_item(item=fetched_item, customization_options=customization_options, **kwargs)
        else:
            return fetched_item

    @classmethod
    def fetch_item(cls, sku, **kwargs):
        raise NotImplementedError()

    @classmethod
    def customize_item(cls, item, customization_options, **kwargs):
        raise NotImplementedError()
