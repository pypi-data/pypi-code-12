# -*- coding: utf-8 -*-
"""
    koalaecommerce.basepricing.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Base implementations of price modifiers. These are in a separate module so as to avoid cyclic import errors.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import operator
import decimal
import prices
from satchless.item import Item
from collections import namedtuple


# Base Price
class Price(prices.Price):
    """
    Overriding the Price class in Satchless to coerce float values to strings before converting to Decimal.
    This ensures that the equality functions act as you would expect when working with currency.
    """
    def __new__(cls, net=None, gross=None, currency=None, history=None):
        if isinstance(net, float):
            net = str(net)
        if gross is not None and isinstance(gross, float):
            gross = str(gross)
        elif gross is None:
            gross = net
        return super(Price, cls).__new__(cls, net=net, gross=gross, currency=currency, history=history)


# Base Modifiers
class BaseItemModifier(prices.PriceModifier):
    modifier_group = 'surcharges'

    def __init__(self, admin_override=False, **kwargs):
        self.admin_override = admin_override

    def applicable(self, item):
        raise NotImplementedError()

    @staticmethod
    def applies_to_order(order):
        return False


class Tax(BaseItemModifier):
    modifier_group = 'tax'
    """
    A generic tax class, provided so all taxers have a common base.
    """

    def apply(self, price_obj):
        history = prices.History(price_obj, operator.__add__, self)
        new_price = Price(net=price_obj.net,
                          gross=(price_obj.gross + self.calculate_tax(price_obj)),
                          currency=price_obj.currency, history=history)
        return new_price

    def calculate_tax(self, price_obj):
        raise NotImplementedError()


class LinearTax(Tax):
    """
    Adds a certain fraction on top of the price.
    """

    def __init__(self, multiplier, name=None, **kwargs):
        if isinstance(multiplier, float):
            multiplier = str(multiplier)
        self.multiplier = decimal.Decimal(multiplier)
        self.name = name or self.name
        super(LinearTax, self).__init__(**kwargs)

    def __repr__(self):
        return 'LinearTax(%r, name=%r)' % (str(self.multiplier), self.name)

    def __lt__(self, other):
        if not isinstance(other, LinearTax):
            raise TypeError('Cannot compare lineartax to %r' % (other,))
        return self.multiplier < other.multiplier

    def __eq__(self, other):
        if isinstance(other, LinearTax):
            return (self.multiplier == other.multiplier and
                    self.name == other.name)
        return False

    def __ne__(self, other):
        return not self == other

    def calculate_tax(self, price_obj):
        return price_obj.gross * self.multiplier

    def applicable(self, item):
        # if self.admin_override:
        # return True
        return True if isinstance(item, Item) else False


class Surcharge(BaseItemModifier):
    """
    Adds a set amount to the base price
    """

    def __init__(self, amount, name=None, **kwargs):
        if isinstance(amount, float):
            amount = str(amount)
        self.amount = decimal.Decimal(amount)
        self.name = name or self.name
        super(Surcharge, self).__init__(**kwargs)

    def __repr__(self):
        return 'Surcharge(%r, name=%r)' % (self.amount, self.name)

    def apply(self, price_obj):
        if price_obj.currency != self.amount.currency:
            raise ValueError('Cannot apply a surcharge in %r to a price in %r' %
                             (self.amount.currency, price_obj.currency))
        history = prices.History(price_obj, operator.__add__, self)
        return Price(net=price_obj.net + self.amount.net,
                     gross=price_obj.gross + self.amount.gross,
                     currency=price_obj.currency, history=history)


class MinimumFee(BaseItemModifier):
    modifier_group = 'minimum_fees'
    """
    Adds a set amount to the base price
    """

    def __init__(self, fee, name=None, **kwargs):
        self.fee = fee
        self.name = name or self.name
        super(MinimumFee, self).__init__(**kwargs)

    def __repr__(self):
        return 'MinimumFee(%r, name=%r)' % (self.fee, self.name)

    def apply(self, price_obj):
        if price_obj.currency != self.fee.currency:
            raise ValueError('Cannot apply a minimum fee in %r to a price in %r' %
                             (self.fee.currency, price_obj.currency))

        if price_obj < self.fee:
            history = prices.History(price_obj, operator.__add__, self)
            return Price(net=self.fee.net,
                         gross=self.fee.gross,
                         currency=self.fee.currency, history=history)
        else:
            return price_obj


class FixedDiscount(BaseItemModifier):
    modifier_group = 'discounts'
    """
    Adds a fixed amount to the price.
    """

    def __init__(self, amount, name=None, **kwargs):
        self.amount = amount
        self.name = name or self.name
        super(FixedDiscount, self).__init__(**kwargs)

    def __repr__(self):
        return 'FixedDiscount(%r, name=%r)' % (self.amount, self.name)

    def apply(self, price_obj):
        if price_obj.currency != self.amount.currency:
            raise ValueError('Cannot apply a discount in %r to a price in %r' %
                             (self.amount.currency, price_obj.currency))
        history = prices.History(price_obj, operator.__add__, self)
        return Price(net=price_obj.net - self.amount.net,
                     gross=price_obj.gross - self.amount.gross,
                     currency=price_obj.currency, history=history)


ItemModifiers = namedtuple('ItemModifiers', 'discounts minimum_fees surcharges tax')


class BasePricingManager(object):
    @classmethod
    def get_all(cls, order, **kwargs):
        modifiers = cls._get_active_modifiers(**kwargs)
        return cls._get_valid_modifiers_for_order(order=order, modifiers=modifiers, **kwargs)

    @classmethod
    def _get_active_modifiers(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def _get_valid_modifiers_for_order(cls, order, modifiers, **kwargs):
        if not modifiers:
            return []

        mod_dict = ItemModifiers([], [], [], [])._asdict()

        for mod in modifiers:
            if mod.applies_to_order(order=order):
                if mod.modifier_group == 'tax':
                    mod_dict[mod.modifier_group] = mod()
                else:
                    if not mod_dict.get(mod.modifier_group):
                        mod_dict[mod.modifier_group] = []

                    mod_dict[mod.modifier_group].append(mod())

        return ItemModifiers(**mod_dict)
