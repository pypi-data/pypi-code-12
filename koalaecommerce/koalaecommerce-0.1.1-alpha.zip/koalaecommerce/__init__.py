# -*- coding: utf-8 -*-
"""
    koalaecommerce.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Koala ecommerce module.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import koalacore
from blinker import signal
from google.appengine.ext import ndb
import datetime
import random
import string
import decimal
import config.inventory
import config.price_modifiers
from satchless.item import Item
from satchless.cart import Cart, CartLine
from koalaecommerce.baseinventory import CustomisableItem, CustomisableStockedItem
from koalaecommerce.basepricing import ItemModifiers, Price
from koalaecommerce.paymentgateways import SagePay, BACS, Cheque
from google.appengine.ext import deferred
from itsdangerous import URLSafeSerializer


__author__ = 'Matt Badger'


# Basket
class PatchedCartLine(CartLine):
    def get_quantity(self, **kwargs):
        return self.quantity


class CustomisableCartLine(CartLine):
    _cache_get_total = None
    modified = False

    def __init__(self, product, quantity=0):
        self.customisations = []

        super(CustomisableCartLine, self).__init__(product=product, quantity=quantity, data=None)

    def __eq__(self, other):
        if not isinstance(other, CustomisableCartLine):
            return NotImplemented

        return (self.product == other.product and
                self.quantity == other.quantity and
                self.customisations == other.customisations)

    def __repr__(self):
        return 'CustomisableCartLine(product=%r, quantity=%r, customisations=%r)' % (self.product, self.quantity, self.customisations)

    def __getstate__(self):
        return (self.product, self.quantity, self.customisations)

    def __setstate__(self, data):
        self.product, self.quantity, self.customisations = data

    def get_quantity(self, **kwargs):
        return self.quantity

    def get_customisation_id(self, customisation):
        return self.customisations.index(customisation)

    def add_customised(self, customisation):
        # TODO: check customisation type?
        self.customisations.append(customisation)
        self.update_quantity()
        self.modified = True

    def delete_customised(self, customisation_id):
        del self.customisations[customisation_id]
        self.update_quantity()
        self.modified = True

    def edit_customised(self, order_item_id, customisation):
        self.customisations[order_item_id] = customisation

    def update_quantity(self):
        self.quantity = len(self.customisations)
        self.modified = True

    def get_total(self, force_reload=False, **kwargs):
        # TODO: add in ability to apply item modifiers to the entire cart line e.g. buy 5 for the price of 4
        # This may involve not calculating tax per item upfront but on the basket as a whole. Have an 'tax exempt' flag?

        if self._cache_get_total and not self.modified and not force_reload:
            return self._cache_get_total
        else:
            total = self.get_price_per_item(**kwargs) * self.get_quantity()
            self._cache_get_total = total
            self.modified = False
            return total


class Basket(Cart):
    # TODO: method to filter a list of price modifiers based on config data
    # TODO: method to setup price modifiers for cart
    def __init__(self, items=None, item_modifiers=None):
        self.admin_override = False
        self._promo_codes = []
        if item_modifiers and isinstance(item_modifiers, ItemModifiers):
            self.item_modifiers = item_modifiers
        else:
            self.item_modifiers = None
        super(Basket, self).__init__(items=items)

    def __getstate__(self):
        # return a tuple as __getstate__ *must* return a truthy value
        out_state = {
            'state': self._state,
            'admin_override': self.admin_override,
            'promo': self._promo_codes,
            'mods': self.item_modifiers,
        }
        return out_state

    def __setstate__(self, state):
        self._state = state['state']
        self.admin_override = state.get('admin_override', False)
        self._promo_codes = state['promo']
        self.item_modifiers = state['mods']
        self.modified = False

    def get_product_customisation(self, basket_index, customisation_index):
        product_line = self.get_product_line(order_product_index=basket_index)

        if not isinstance(product_line, CustomisableCartLine):
            raise TypeError('Cart line is not of type CustomisableCartLine')

        return product_line.customisations[customisation_index]

    def get_product_line(self, order_product_index):
        return self._state[order_product_index]

    def create_line(self, product, quantity, data):
        return PatchedCartLine(product, quantity, data=data)

    @staticmethod
    def create_customised_line(product, quantity=0):
        return CustomisableCartLine(product=product, quantity=quantity)

    def get_customisable_line(self, product):
        return next(
            (cart_line for cart_line in self._state
             if cart_line.product == product),
            None)

    def _get_or_create_customisable_line(self, product):
        cart_line = self.get_customisable_line(product)
        if cart_line:
            return (False, cart_line)
        else:
            return (True, self.create_customised_line(product))

    @staticmethod
    def decode_order_item_key(basket_item_key):
        basket_index, customisation_index = basket_item_key.split('-')
        return int(basket_index), int(customisation_index)

    @staticmethod
    def encode_order_item_key(basket_index, customisation_index):
        return '{0}-{1}'.format(basket_index, customisation_index)

    def add_normal_product(self, product, quantity=1, data=None, replace=False, check_quantity=True):
        created, cart_line = self._get_or_create_line(product, 0, data)

        if replace:
            new_quantity = quantity
        else:
            new_quantity = cart_line.quantity + quantity

        if new_quantity < 0:
            raise ValueError('%r is not a valid quantity (results in %r)' % (
                quantity, new_quantity))

        if check_quantity:
            self.check_quantity(product, new_quantity, data)

        cart_line.quantity = new_quantity

        if not cart_line.quantity and not created:
            self._state.remove(cart_line)
            self.modified = True
        elif cart_line.quantity and created:
            self._state.append(cart_line)
            self.modified = True
        elif not created:
            self.modified = True

    def add_customisable_product(self, product, customisation, quantity=1, check_quantity=True):
        created, cart_line = self._get_or_create_customisable_line(product)

        new_quantity = cart_line.quantity + quantity

        if quantity < 1:
            raise ValueError('%r is not a valid quantity to add (results in %r)' % (
                quantity, new_quantity))

        if check_quantity:
            self.check_quantity(product, new_quantity, None)

        cart_line.add_customised(customisation=customisation)

        if created:
            self._state.append(cart_line)

        self.modified = True

    def add(self, product, **kwargs):
        if isinstance(product, CustomisableItem) or isinstance(product, CustomisableStockedItem):
            self.add_customisable_product(product, **kwargs)
        elif isinstance(product, Item):
            self.add_normal_product(product, **kwargs)
        else:
            raise TypeError('Unrecognised product type')

    def edit_customisable_product(self, basket_item_key, new_customisation):
        basket_index, customisation_index = self.decode_order_item_key(basket_item_key=basket_item_key)

        cart_line = self.get_product_line(order_product_index=basket_index)

        if not isinstance(cart_line, CustomisableCartLine):
            raise TypeError('Cartline is not editable')

        cart_line.edit_customised(order_item_id=customisation_index, customisation=new_customisation)

        self.modified = True

    edit = edit_customisable_product

    def remove_customisable_product(self, basket_item_key):
        quantity = -1
        basket_index, customisation_index = self.decode_order_item_key(basket_item_key=basket_item_key)
        cart_line = self.get_product_line(order_product_index=basket_index)
        new_quantity = cart_line.quantity + quantity

        if new_quantity < 0:
            raise ValueError('%r is not a valid quantity to remove (results in %r)' % (
                quantity, new_quantity))

        if not new_quantity:
            del self._state[basket_index]
        else:
            cart_line.delete_customised(customisation_id=customisation_index)

        self.modified = True

    def remove(self, **kwargs):
        if kwargs.get('basket_item_key', False):
            self.remove_customisable_product(**kwargs)
        elif kwargs.get('product', False) and isinstance(kwargs['product'], CartLine):
            kwargs['quantity'] = -1
            self.add_normal_product(**kwargs)
        else:
            raise ValueError('Remove method not supported')

    def get_total(self, **kwargs):
        eval_date = getattr(self, 'payment_date', datetime.datetime.now())
        return super(Basket, self).get_total(item_modifiers=self.item_modifiers, promo_codes=self._promo_codes, force_reload=self.modified, admin_override=self.admin_override, eval_date=eval_date)

    def add_promo_code(self, promo_code):
        # TODO: change the promo code attr to be a set, not a list
        if not self._promo_codes:
            self._promo_codes = set()
        self._promo_codes.add(promo_code)
        self.modified = True

    def remove_promo_code(self, promo_code):
        if not self._promo_codes:
            self._promo_codes = set()
        self._promo_codes.remove(promo_code)
        self.modified = True

    def update_modifiers(self, modifiers):
        self.item_modifiers = modifiers
        self.modified = True


# API Def
class Customer(object):
    def __init__(self, customer_uid, first_name, last_name, email, user_uid=None, company_name=None, phone=None, turnover_ltm=False, tax_number=None, membership_number=None):
        self.customer_uid = customer_uid
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.user_uid = user_uid
        self.company_name = company_name
        self.phone = phone
        self.turnover_ltm = turnover_ltm
        self.tax_number = tax_number
        self.membership_number = membership_number


class Address(object):
    def __init__(self, country, city, address_1, address_2=None, state=None, post_code=None):
        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.country = country


# TODO: add customer name computed property that includes the company name, if available
class Order(koalacore.Resource):
    # Order
    order_reference = koalacore.ResourceProperty(title=u'Order Reference')
    order_type = koalacore.ResourceProperty(title=u'Order Type', default='default')
    order_status = koalacore.ResourceProperty(title=u'Order Status', default='INVOICED')
    order_started = koalacore.ResourceProperty(title=u'Order Started')
    order_complete = koalacore.ResourceProperty(title=u'Order Complete')
    # Customer
    customer_uid = koalacore.ResourceProperty(title=u'Customer UID')
    user_uid = koalacore.ResourceProperty(title=u'User UID')
    customer_first_name = koalacore.ResourceProperty(title=u'Customer First Name')
    customer_last_name = koalacore.ResourceProperty(title=u'Customer Last Name')
    customer_company_name = koalacore.ResourceProperty(title=u'Customer Company Name')
    customer_email = koalacore.ResourceProperty(title=u'Customer Email')
    customer_phone = koalacore.ResourceProperty(title=u'Customer Phone')
    customer_turnover_ltm = koalacore.ResourceProperty(title=u'Customer Turnover < £1M')
    customer_tax_number = koalacore.ResourceProperty(title=u'Customer Tax Number')
    customer_membership_number = koalacore.ResourceProperty(title=u'Customer Membership Number')
    customer = koalacore.ComputedResourceProperty(title=u'Customer', compute_function=lambda resource: Customer(resource.customer_uid, resource.customer_first_name, resource.customer_last_name, resource.customer_email, resource.user_uid, resource.customer_company_name, resource.customer_phone, resource.customer_turnover_ltm, resource.customer_tax_number, resource.customer_membership_number))
    # Delivery Address
    delivery_address_1 = koalacore.ResourceProperty(title=u'Delivery Address 1')
    delivery_address_2 = koalacore.ResourceProperty(title=u'Delivery Address 2')
    delivery_city = koalacore.ResourceProperty(title=u'Delivery City')
    delivery_country = koalacore.ResourceProperty(title=u'Delivery Country')
    delivery_state = koalacore.ResourceProperty(title=u'Delivery State')
    delivery_post_code = koalacore.ResourceProperty(title=u'Delivery Post Code')
    delivery_address = koalacore.ComputedResourceProperty(title=u'Delivery Address', compute_function=lambda resource: Address(resource.delivery_country, resource.delivery_city, resource.delivery_address_1, resource.delivery_address_2, resource.delivery_state, resource.delivery_post_code))
    # Billing Address
    billing_address_1 = koalacore.ResourceProperty(title=u'Billing Address 1')
    billing_address_2 = koalacore.ResourceProperty(title=u'Billing Address 2')
    billing_city = koalacore.ResourceProperty(title=u'Billing City')
    billing_country = koalacore.ResourceProperty(title=u'Billing Country')
    billing_state = koalacore.ResourceProperty(title=u'Billing State')
    billing_post_code = koalacore.ResourceProperty(title=u'Billing Post Code')
    billing_address = koalacore.ComputedResourceProperty(title=u'Billing Address', compute_function=lambda resource: Address(resource.billing_country, resource.billing_city, resource.billing_address_1, resource.billing_address_2, resource.billing_state, resource.billing_post_code))
    # Payment
    basket = koalacore.ResourceProperty(title=u'Basket')
    total = koalacore.ResourceProperty(title=u'Order Total')
    currency = koalacore.ResourceProperty(title=u'Currency')
    payment_details = koalacore.ResourceProperty(title=u'Payment Details')
    payment_completed_by = koalacore.ResourceProperty(title=u'Completed By UID')
    payment_completed_by_name = koalacore.ResourceProperty(title=u'Completed By')

    def __init__(self, **kwargs):
        # We only want to generate a new reference if one is missing or if order is not complete.
        if 'order_reference' not in kwargs or not kwargs['order_reference']:
            kwargs['order_reference'] = self.generate_order_reference()

        if 'basket' not in kwargs or not isinstance(kwargs['basket'], Basket):
            kwargs['basket'] = Basket()

        super(Order, self).__init__(**kwargs)

    @staticmethod
    def generate_order_reference():
        random_token = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(5)])
        return 'GT16-{0}{1}'.format(random_token, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    def update_order_reference(self):
        self.order_reference = self.generate_order_reference()

    def validate(self):
        valid = True

        if not self.uid:
            valid = False

        if not self.order_reference:
            valid = False

        if not self.customer_uid:
            valid = False

        if not self.customer_first_name:
            valid = False

        if not self.customer_last_name:
            valid = False

        if not self.customer_email:
            valid = False

        if not self.delivery_address_1:
            valid = False

        if not self.delivery_city:
            valid = False

        if not self.delivery_country:
            valid = False

        if not self.billing_address_1:
            valid = False

        if not self.billing_city:
            valid = False

        if not self.billing_country:
            valid = False

        if not self.basket:
            valid = False
        elif self.basket and not self.basket.count():
            valid = False

        return valid

    def to_search_doc(self):
        payment_method = 'n/a'
        if self.payment_details is not None:
            payment_method = self.payment_details.method

        if self.payment_details is not None and (isinstance(self.payment_details.timestamp, datetime.date) or isinstance(self.payment_details.timestamp, datetime.datetime)):
            payment_date = [
                koalacore.GAESearchInterface.date_field(name='payment_date', value=self.payment_details.timestamp),
                koalacore.GAESearchInterface.atom_field(name='payment_year', value=str(self.payment_details.timestamp.year)),
                koalacore.GAESearchInterface.atom_field(name='payment_month', value=str(self.payment_details.timestamp.month)),
            ]
        else:
            payment_date = [koalacore.GAESearchInterface.atom_field(name='payment_date', value='NA')]

        if isinstance(self.order_started, datetime.date) or isinstance(self.order_started, datetime.datetime):
            started_date = [
                koalacore.GAESearchInterface.date_field(name='started_date', value=self.order_started),
                koalacore.GAESearchInterface.atom_field(name='started_year', value=str(self.order_started.year)),
                koalacore.GAESearchInterface.atom_field(name='started_month', value=str(self.order_started.month)),
            ]
        else:
            started_date = [
                koalacore.GAESearchInterface.atom_field(name='started_date', value='NA'),
                koalacore.GAESearchInterface.atom_field(name='started_year', value='NA'),
                koalacore.GAESearchInterface.atom_field(name='started_month', value='NA'),
            ]

        total = 0
        if self.basket is not None and self.basket.count():
            basket_total = self.basket.get_total()
            total = float(basket_total.gross)

        return [
            koalacore.GAESearchInterface.atom_field(name='order_reference', value=self.order_reference),
            koalacore.GAESearchInterface.atom_field(name='order_type', value=self.order_type),
            koalacore.GAESearchInterface.atom_field(name='order_status', value=self.order_status),
            koalacore.GAESearchInterface.atom_field(name='order_complete', value='Yes' if self.order_complete else 'No'),
            koalacore.GAESearchInterface.atom_field(name='customer_uid', value=self.customer_uid),
            koalacore.GAESearchInterface.atom_field(name='user_uid', value=self.user_uid),
            koalacore.GAESearchInterface.atom_field(name='customer_first_name', value=self.customer_first_name),
            koalacore.GAESearchInterface.atom_field(name='customer_last_name', value=self.customer_last_name),
            koalacore.GAESearchInterface.atom_field(name='customer_company_name', value=self.customer_company_name),
            koalacore.GAESearchInterface.atom_field(name='customer_email', value=self.customer_email),
            koalacore.GAESearchInterface.atom_field(name='customer_phone', value=self.customer_phone),
            koalacore.GAESearchInterface.atom_field(name='customer_turnover_ltm', value='Yes' if self.customer_turnover_ltm else 'No'),
            koalacore.GAESearchInterface.atom_field(name='customer_tax_number', value=self.customer_tax_number if self.customer_tax_number else 'No'),
            koalacore.GAESearchInterface.atom_field(name='customer_membership_number', value=self.customer_membership_number if self.customer_membership_number else 'No'),
            koalacore.GAESearchInterface.atom_field(name='delivery_address_1', value=self.delivery_address_1),
            koalacore.GAESearchInterface.atom_field(name='delivery_address_2', value=self.delivery_address_2),
            koalacore.GAESearchInterface.atom_field(name='delivery_city', value=self.delivery_city),
            koalacore.GAESearchInterface.atom_field(name='delivery_country', value=self.delivery_country),
            koalacore.GAESearchInterface.atom_field(name='delivery_state', value=self.delivery_state),
            koalacore.GAESearchInterface.atom_field(name='delivery_post_code', value=self.delivery_post_code),
            koalacore.GAESearchInterface.atom_field(name='billing_address_1', value=self.billing_address_1),
            koalacore.GAESearchInterface.atom_field(name='billing_address_2', value=self.billing_address_2),
            koalacore.GAESearchInterface.atom_field(name='billing_city', value=self.billing_city),
            koalacore.GAESearchInterface.atom_field(name='billing_country', value=self.billing_country),
            koalacore.GAESearchInterface.atom_field(name='billing_state', value=self.billing_state),
            koalacore.GAESearchInterface.atom_field(name='billing_post_code', value=self.billing_post_code),
            koalacore.GAESearchInterface.number_field(name='total', value=total if total else 0),
            koalacore.GAESearchInterface.atom_field(name='currency', value=self.currency),
            koalacore.GAESearchInterface.atom_field(name='payment_method', value=payment_method),
            koalacore.GAESearchInterface.atom_field(name='payment_completed_by', value=self.payment_completed_by),
            koalacore.GAESearchInterface.atom_field(name='payment_completed_by_name', value=self.payment_completed_by_name),
            koalacore.GAESearchInterface.text_field(name='fuzzy_order_reference', value=koalacore.generate_autocomplete_tokens(original_string=self.order_reference)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_customer_first_name', value=koalacore.generate_autocomplete_tokens(original_string=self.customer_first_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_customer_last_name', value=koalacore.generate_autocomplete_tokens(original_string=self.customer_last_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_customer_company_name', value=koalacore.generate_autocomplete_tokens(original_string=self.customer_company_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_payment_completed_by_name', value=koalacore.generate_autocomplete_tokens(original_string=self.payment_completed_by_name)),
        ] + payment_date + started_date


class NDBOrder(koalacore.NDBResource):
    # Order
    order_reference = ndb.StringProperty('or', indexed=False)
    order_status = ndb.StringProperty('osttl', default='INVOICED', indexed=False)
    order_started = ndb.DateTimeProperty('ostrt', indexed=False)
    order_type = ndb.StringProperty('ot', indexed=True)
    order_complete = ndb.BooleanProperty('oc', default=False, indexed=True)
    # Customer
    customer_uid = ndb.KeyProperty('ocuid', indexed=True)
    user_uid = ndb.StringProperty('ouuid', indexed=False)
    customer_first_name = ndb.StringProperty('ocfn', indexed=False)
    customer_last_name = ndb.StringProperty('ocln', indexed=False)
    customer_company_name = ndb.StringProperty('occn', indexed=False)
    customer_email = ndb.StringProperty('oce', indexed=False)
    customer_phone = ndb.StringProperty('ocp', indexed=False)
    customer_turnover_ltm = ndb.BooleanProperty('octltm', default=False, indexed=False)
    customer_tax_number = ndb.StringProperty('octn', indexed=False)
    customer_membership_number = ndb.StringProperty('ocmn', indexed=False)
    # Delivery Address
    delivery_address_1 = ndb.StringProperty('oda1', indexed=False)
    delivery_address_2 = ndb.StringProperty('oda2', indexed=False)
    delivery_city = ndb.StringProperty('odc', indexed=False)
    delivery_country = ndb.StringProperty('odctry', indexed=False)
    delivery_state = ndb.StringProperty('ods', indexed=False)
    delivery_post_code = ndb.StringProperty('odpc', indexed=False)
    # Billing Address
    billing_address_1 = ndb.StringProperty('oba1', indexed=False)
    billing_address_2 = ndb.StringProperty('oba2', indexed=False)
    billing_city = ndb.StringProperty('obac', indexed=False)
    billing_country = ndb.StringProperty('obactry', indexed=False)
    billing_state = ndb.StringProperty('obs', indexed=False)
    billing_post_code = ndb.StringProperty('obpc', indexed=False)
    # Payment
    basket = ndb.PickleProperty('ob', indexed=False)
    total = ndb.FloatProperty('ottl', indexed=False)
    currency = ndb.StringProperty('ocrrncy', indexed=False)
    payment_details = ndb.PickleProperty('opd', indexed=False)
    payment_completed_by = ndb.StringProperty('opcb', indexed=False)
    payment_completed_by_name = ndb.StringProperty('opcbn', indexed=False)


class OrderSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'orders'


class OrderNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBOrder
    _resource_object = Order

    @classmethod
    def _internal_get_customer_orders(cls, customer_uid, order_type=None, order_complete=None, **kwargs):
        if order_complete is not None and not isinstance(order_complete, bool):
            raise ValueError('order_complete must be a boolean')

        if order_type is not None and order_complete is not None:
            op_result = cls._datastore_model.query(ndb.AND(cls._datastore_model.customer_uid == customer_uid, cls._datastore_model.order_type == order_type, cls._datastore_model.order_complete == order_complete)).fetch_async()
        elif order_type is not None:
            op_result = cls._datastore_model.query(ndb.AND(cls._datastore_model.customer_uid == customer_uid, cls._datastore_model.order_type == order_type)).fetch_async()
        elif order_complete is not None:
            op_result = cls._datastore_model.query(ndb.AND(cls._datastore_model.customer_uid == customer_uid, cls._datastore_model.order_complete == order_complete)).fetch_async()
        else:
            op_result = cls._datastore_model.query(cls._datastore_model.customer_uid == customer_uid).fetch_async()
        # TODO: query cursor support
        op_result.method = 'get_async'

        return op_result

    @classmethod
    def get_customer_orders_async(cls, customer_uid, order_type=None, order_complete=None, **kwargs):
        """
        This is just to keep consistency with the Koala datastore class. It isn't actually necessary because we don't
        have to do any conversion on the method args.

        :param customer_uid:
        :param order_type:
        :param order_complete:
        :returns future:
        """
        return cls._internal_get_customer_orders(customer_uid=cls._convert_string_to_ndb_key(datastore_key=customer_uid),
                                                 order_type=order_type,
                                                 order_complete=order_complete, **kwargs)

    @classmethod
    def get_customer_orders(cls, customer_uid, order_type=None, order_complete=None, **kwargs):
        """
        Wrapper around get_customer_orders_async to automatically resolve async future. May be overridden.

        :param customer_uid:
        :param order_type:
        :param order_complete:
        :returns resource_object, or None:
        """
        entity_future = cls.get_customer_orders_async(customer_uid=customer_uid,
                                                      order_type=order_type,
                                                      order_complete=order_complete)
        return cls.get_future_result(entity_future)


class Orders(koalacore.BaseAPI):
    _api_name = 'order'
    _api_model = Order
    _datastore_interface = OrderNDBInterface
    _search_interface = OrderSearchInterface

    @classmethod
    def get_by_customer_uid(cls, customer_uid, order_type=None, order_complete=None, **kwargs):
        if signal('pre_get_by_customer_uid').has_receivers_for(cls):
            signal('pre_get_by_customer_uid').send(cls,
                                                   customer_uid=customer_uid,
                                                   order_type=order_type,
                                                   order_complete=order_complete, **kwargs)

        resources = cls._datastore_interface.get_customer_orders(customer_uid=customer_uid,
                                                                 order_type=order_type,
                                                                 order_complete=order_complete, **kwargs)

        if signal('post_get_by_customer_uid').has_receivers_for(cls):
            signal('post_get_by_customer_uid').send(cls,
                                                    result=resources,
                                                    customer_uid=customer_uid,
                                                    order_type=order_type,
                                                    order_complete=order_complete, **kwargs)

        return resources

    @classmethod
    def complete_order(cls, payment_response, completed_by_uid, completed_by_name, **kwargs):
        if signal('pre_complete_order').has_receivers_for(cls):
            signal('pre_complete_order').send(cls, payment_response=payment_response, **kwargs)

        if not payment_response.success:
            raise ValueError('The supplied payment response was not successful; can\'t complete order.')

        order = cls._datastore_interface.get(resource_uid=payment_response.order_uid, **kwargs)
        if not order:
            raise ValueError('The supplied payment response is not valid; order_uid does not exist')

        if not order.validate():
            raise ValueError('Order is not valid. Usually because the basket is empty.')

        if order.order_reference != payment_response.order_reference:
            raise ValueError('The supplied payment response is not valid; order_reference mismatch')

        if order.basket.get_total().gross != decimal.Decimal(payment_response.amount):
            raise ValueError('The supplied payment response is not valid; amount mismatch')

        if order.order_complete:
            raise ValueError('The supplied payment response is not valid; order already complete')

        order.order_complete = True
        order.order_status = 'PAID'
        order.payment_details = payment_response
        order.payment_completed_by = completed_by_uid
        order.payment_completed_by_name = completed_by_name

        resource_uid = cls._datastore_interface.update(resource_object=order, **kwargs)
        deferred.defer(cls._update_search_index, resource_uid=resource_uid, _queue='search-index-update')

        if signal('post_complete_order').has_receivers_for(cls):
            signal('post_complete_order').send(cls, result=resource_uid, payment_response=payment_response, **kwargs)

        return resource_uid


def _block_completed_order_modification(sender, resource_object, **kwargs):
    if resource_object.order_complete:
        raise ValueError('Orders cannot be marked as completed. Please use the dedicated complete_order method')


signal('pre_insert').connect(_block_completed_order_modification, sender=Orders)
signal('pre_update').connect(_block_completed_order_modification, sender=Orders)


def _block_completed_order_deletion(sender, resource_uid, **kwargs):
    order = OrderNDBInterface.get(resource_uid=resource_uid)
    if order.order_complete:
        raise ValueError('Completed orders cannot be deleted.')


signal('pre_delete').connect(_block_completed_order_deletion, sender=Orders)


class Inventory(object):
    _api_name = 'inventory'

    @classmethod
    def get(cls, sku, customization_options=None, **kwargs):
        signal('get.hook').send(cls, sku=sku)
        return config.inventory.InventoryManager.get_inventory_item(sku=sku, customization_options=customization_options, **kwargs)


class Pricing(object):
    _api_name = 'pricing'

    @classmethod
    def get_all(cls, order, **kwargs):
        signal('get.hook').send(cls, order=order)
        return config.price_modifiers.PricingManager.get_all(order=order, **kwargs)


class Payments(object):
    _signature_salt = 'sign-payment-request-salt'

    @classmethod
    def new(cls, order, payment_config, additional_signature_kwargs=None, **kwargs):
        """
        It's up to the payment gateway what it wants with the request signature, but it must be present to validate a
        payment.
        :param order:
        :param payment_config:
        :param additional_signature_kwargs:
        :param kwargs:
        :return:
        """
        if order is None or payment_config is None:
            raise ValueError('order and gateway_config are all required arguments')

        # TODO: run validator on order. For now just call the validate method in order, but later provide a more robust
        # check that is not reliant on the order model
        if not order.validate():
            raise ValueError('Order is not valid')

        signature = {'order_uid': order.uid, 'order_reference': order.order_reference}

        if additional_signature_kwargs is not None:
            signature.update(additional_signature_kwargs)

        request_signature = _encrypt_response(message=signature,
                                              key=payment_config['request_signing_key'],
                                              salt=cls._signature_salt)

        if payment_config['payment_gateway'] == 'sagepay' or payment_config['payment_gateway'] == 'sagepay_test':
            return request_signature, SagePay.generate_request(request_signature=request_signature, order=order,
                                                               gateway_config=payment_config, **kwargs)
        elif payment_config['payment_gateway'] == 'bacs':
            return request_signature, BACS.generate_request(request_signature=request_signature, order=order,
                                                            gateway_config=payment_config, **kwargs)
        elif payment_config['payment_gateway'] == 'cheque':
            return request_signature, Cheque.generate_request(request_signature=request_signature, order=order,
                                                              gateway_config=payment_config, **kwargs)
        else:
            raise ValueError('Payment Gateway not supported')

    @classmethod
    def list(cls, auth, order):
        # TODO: Get list of enabled providers from config
        # payment_options = cls.get_user_privileges(user_sec_ob=auth, entity_sec_ob=cls._mock_security_object())
        #
        # providers = []
        # for option in payment_options:
        #     payment_gateway = ACTIVE_PAYMENT_GATEWAY_MAP.get(option, False)
        #     if payment_gateway and isinstance(payment_gateway, BasePaymentGateway):
        #         providers.append(payment_gateway.generate_request(order=order))
        #
        # return providers
        pass

    @classmethod
    def verify_response(cls, request_signature, gateway_response, payment_config, **kwargs):
        decrypted_signature = _decrypt_response(serialized=request_signature,
                                                key=payment_config['request_signing_key'],
                                                salt=cls._signature_salt)

        if payment_config['payment_gateway'] == 'sagepay' or payment_config['payment_gateway'] == 'sagepay_test':
            response = SagePay.process_response(gateway_response=gateway_response, gateway_config=payment_config, **kwargs)
        elif payment_config['payment_gateway'] == 'bacs':
            response = BACS.process_response(gateway_response=gateway_response, gateway_config=payment_config, **kwargs)
        elif payment_config['payment_gateway'] == 'cheque':
            response = Cheque.process_response(gateway_response=gateway_response, gateway_config=payment_config, **kwargs)
        else:
            raise ValueError('Payment Gateway not supported')

        if decrypted_signature['order_reference'] != response.order_reference:
            raise ValueError('Request signature does not match the payment gateway response. Something is afoot...')

        response.order_uid = decrypted_signature['order_uid']
        return response, decrypted_signature


def _encrypt_response(message, key, salt):
    signer = URLSafeSerializer(secret_key=key, salt=salt)
    return signer.dumps(message)


def _decrypt_response(serialized, key, salt):
    signer = URLSafeSerializer(secret_key=key, salt=salt)
    return signer.loads(serialized)
