import unittest
import koalaecommerce
from google.appengine.ext import testbed
from google.appengine.ext import deferred
from datetime import datetime, date
from google.appengine.ext import ndb
from satchless.item import Item as satchlessitem
import decimal
import config
# Analytics
import urllib
import uuid
from google.appengine.api import urlfetch


__author__ = 'Matt'


ALLOW_BROWSER_TESTING = True
DEFAULT_ORDER_STATUS = 'INVOICED'


STARTED_DATE = datetime.now()
TEST_CUSTOMER_UID = ndb.Key('GFFCompany', 'test_company_uid').urlsafe()

VALID_UK_ORDER = {
    'order_type': 'test_order_type',
    'order_started': STARTED_DATE,
    'order_complete': False,
    'customer_uid': TEST_CUSTOMER_UID,
    'user_uid': 'test_user_uid',
    'customer_first_name': 'test_customer_first_name',
    'customer_last_name': 'test_customer_last_name',
    'customer_company_name': 'test_customer_company_name',
    'customer_email': 'foss@lighthouseuk.net',
    'customer_phone': '+4412345678',
    'customer_turnover_ltm': False,
    'customer_tax_number': 'test_customer_tax_number',
    'customer_membership_number': 'test_customer_membership_number',
    'delivery_address_1': 'Lighthouse FOSS',
    'delivery_address_2': '',
    'delivery_city': 'Shrewsbury',
    'delivery_country': 'GB',
    'delivery_state': '',
    'delivery_post_code': 'SY1 2AJ',
    'billing_address_1': 'Lighthouse FOSS',
    'billing_address_2': '',
    'billing_city': 'Shrewsbury',
    'billing_country': 'GB',
    'billing_state': '',
    'billing_post_code': 'SY1 2AJ',
    'total': 0,
    'currency': 'GBP',
}

INVALID_ORDER = {
    'order_reference': '',
    'order_type': 'test_order_type',
    'order_started': STARTED_DATE,
    'order_complete': False,
    'customer_uid': TEST_CUSTOMER_UID,
    'user_uid': 'test_user_uid',
    'customer_first_name': '',
    'customer_last_name': 'test_customer_last_name',
    'customer_company_name': 'test_customer_company_name',
    'customer_email': 'test_customer_email',
    'customer_phone': '',
    'customer_turnover_ltm': False,
    'customer_tax_number': 'test_customer_tax_number',
    'customer_membership_number': 'test_customer_membership_number',
    'delivery_address_1': 'test_delivery_address_1',
    'delivery_address_2': 'test_delivery_address_2',
    'delivery_city': 'test_delivery_city',
    'delivery_country': 'test_delivery_country',
    'delivery_state': 'test_delivery_state',
    'delivery_post_code': 'test_delivery_post_code',
    'billing_address_1': 'test_billing_address_1',
    'billing_address_2': 'test_billing_address_2',
    'billing_city': 'test_billing_city',
    'billing_country': '',
    'billing_state': 'test_billing_state',
    'billing_post_code': 'test_billing_post_code',
    'total': 0,
    'currency': 'test_currency',
}

MERCHANT_INFO = {
    'name': 'Lighthouse FOSS',
    'vat_number': '0123454',
    'registered_address': 'Lighthouse FOSS, Address1, Address2, City, County, Country, PostCode',
    'success_message': '<h4>Receipted invoice from {merchant_name} for {customer}</h4><small>Registered Address: {merchant_registered_address}. VAT No.: {merchant_vat_number}</small>',
    'description': 'GT 2015',
    'website': 'https://foss.lighthouseuk.net',
    'notification_emails': 'foss@lighthouseuk.net',
    'send_confirmation': True,
}


REQUEST_SIGNING_KEY = config.secrets.get('payment_request_signing_key')
RESPONSE_SIGNING_KEY = config.secrets.get('payment_response_signing_key')


def _add_test_item_to_basket(order):
    order.basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)


class UncustomizableItem(satchlessitem):
    def get_price_per_item(self, **kwargs):
        return koalaecommerce.Price(net=30, currency='GBP')


class UncustomizableItemTwo(satchlessitem):
    def get_price_per_item(self, **kwargs):
        return koalaecommerce.Price(net=55, currency='GBP')


UNCUSTOMIZABLE_ITEM_ONE = UncustomizableItem()
UNCUSTOMIZABLE_ITEM_TWO = UncustomizableItemTwo()

customization_options_1 = {
    'custom_name': 'Custom Name 1',
}
NORMAL_ITEM_1, EXAMPLE_CUSTOMISATION_ONE = koalaecommerce.Inventory.get(sku='KE-2015-111', customization_options=customization_options_1)


customization_options_2 = {
    'custom_name': 'Custom Name 2',
}
STOCKED_ITEM, EXAMPLE_CUSTOMISATION_TWO = koalaecommerce.Inventory.get(sku='KE-2015-111-si', customization_options=customization_options_2)


class TestBasket(unittest.TestCase):
    def setUp(self):
        pass

    def test_basket_multiple_same_product(self):
        basket = koalaecommerce.Basket()
        basket.add(product=UNCUSTOMIZABLE_ITEM_ONE)

        basket.add(product=UNCUSTOMIZABLE_ITEM_ONE)

        self.assertEqual(len(basket), 1, 'Unique product count incorrect')
        self.assertEqual(basket.count(), 2, 'Basket item count incorrect')
        self.assertEqual(basket.get_total(), koalaecommerce.Price(60, currency='GBP'), 'Basket total incorrect')

    def test_basket_multiple_different_products(self):
        basket = koalaecommerce.Basket()
        basket.add(product=UNCUSTOMIZABLE_ITEM_ONE)
        basket.add(product=UNCUSTOMIZABLE_ITEM_TWO)

        self.assertEqual(len(basket), 2, 'Unique product count incorrect')
        self.assertEqual(basket.count(), 2, 'Basket item count incorrect')
        self.assertEqual(basket.get_total().gross, koalaecommerce.Price(85, currency='GBP').gross, 'Basket total incorrect')

    def test_basket_add_custom_product(self):
        basket = koalaecommerce.Basket()
        basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)

        self.assertEqual(len(basket), 1, 'Unique product count incorrect')
        self.assertEqual(basket.count(), 1, 'Basket item count incorrect')
        self.assertEqual(basket.get_total(), koalaecommerce.Price(69, currency='GBP'), 'Basket total incorrect')

    def test_basket_add_multiple_custom_product(self):
        basket = koalaecommerce.Basket()
        basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)
        basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_TWO)

        self.assertEqual(len(basket), 1, 'Unique product count incorrect')
        self.assertEqual(basket.count(), 2, 'Basket item count incorrect')
        self.assertEqual(basket.get_total(), koalaecommerce.Price(138, currency='GBP'), 'Basket total incorrect')

    def test_basket_edit_custom_product(self):
        basket = koalaecommerce.Basket()
        basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)

        key = basket.encode_order_item_key(0, 0)

        basket.edit(basket_item_key=key, new_customisation=EXAMPLE_CUSTOMISATION_TWO)

        self.assertEqual(len(basket), 1, 'Unique product count incorrect')
        self.assertEqual(basket.count(), 1, 'Basket item count incorrect')
        self.assertEqual(basket.get_total(), koalaecommerce.Price(69, currency='GBP'), 'Basket total incorrect')

        edited_item = basket.get_product_customisation(basket_index=0, customisation_index=0)
        self.assertEqual(edited_item.custom_name, customization_options_2['custom_name'], 'Customisation name does not match expected.')

    def test_basket_remove_custom_product(self):
        basket = koalaecommerce.Basket()
        basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)

        key = basket.encode_order_item_key(0, 0)

        basket.remove(basket_item_key=key)

        self.assertEqual(len(basket), 0, 'Unique product count incorrect')
        self.assertEqual(basket.count(), 0, 'Basket item count incorrect')


class TestPricingManager(unittest.TestCase):
    def setUp(self):
        pass

    def test_uk_vat(self):
        order = koalaecommerce.Orders.new(**VALID_UK_ORDER)
        pricing_modifiers = koalaecommerce.Pricing.get_all(order=order)
        order.basket.update_modifiers(modifiers=pricing_modifiers)

        order.basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)
        order.basket.get_total()

        self.assertEqual(len(order.basket), 1, 'Unique product count incorrect')
        self.assertEqual(order.basket.count(), 1, 'Basket item count incorrect')
        self.assertEqual(order.basket.get_total().net, 69, 'Basket total incorrect')
        self.assertEqual(order.basket.get_total().gross, decimal.Decimal('%.2f' % 82.8), 'Basket total incorrect')


class PaymentGatewayResponse(object):
    def __init__(self, gateway_transaction_uid, order_reference, amount, timestamp, method, encoded_response, success=False, status=None, additional_details=None, order_uid=None):
        # To be set by the payment gateway
        self.gateway_transaction_uid = gateway_transaction_uid
        self.order_reference = order_reference
        self.success = success
        self.timestamp = timestamp
        self.method = method
        self.amount = amount
        self.encoded_response = encoded_response
        self.status = status
        self.additional_details = additional_details
        # To be set by the Payments API
        self.order_uid = order_uid

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


TEST_RESPONSE = PaymentGatewayResponse(gateway_transaction_uid='test_txuid', order_reference='test_ref', amount=10, timestamp=datetime.now(), method='SagePay', encoded_response='encoded_response')
TEST_RESPONSE_2 = PaymentGatewayResponse(gateway_transaction_uid='test_txuid2', order_reference='test_ref2', amount=102, timestamp=datetime.now(), method='SagePay2', encoded_response='encoded_response2')


class TestOrder(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        started_date = datetime.now()
        test_customer_uid = ndb.Key('GFFCompany', 'test_company_uid').urlsafe()
        self.test_order_with_spaces = {
            'order_reference': '  test_order_reference  ',
            'order_type': '  test_order_type  ',
            'order_started': started_date,
            'order_complete': False,
            'customer_uid': test_customer_uid,
            'user_uid': '  test_user_uid  ',
            'customer_first_name': '  test_customer_first_name  ',
            'customer_last_name': '  test_customer_last_name  ',
            'customer_company_name': '  test_customer_company_name  ',
            'customer_email': '  test_customer_email  ',
            'customer_phone': '  test_customer_phone  ',
            'customer_turnover_ltm': False,
            'customer_tax_number': '  test_customer_tax_number  ',
            'customer_membership_number': '  test_customer_membership_number  ',
            'delivery_address_1': '  test_delivery_address_1  ',
            'delivery_address_2': '  test_delivery_address_2  ',
            'delivery_city': '  test_delivery_city  ',
            'delivery_country': '  test_delivery_country  ',
            'delivery_state': '  test_delivery_state  ',
            'delivery_post_code': '  test_delivery_post_code  ',
            'billing_address_1': '  test_billing_address_1  ',
            'billing_address_2': '  test_billing_address_2  ',
            'billing_city': '  test_billing_city  ',
            'billing_country': '  test_billing_country  ',
            'billing_state': '  test_billing_state  ',
            'billing_post_code': '  test_billing_post_code  ',
            'total': 0,
            'currency': '  test_currency  ',
            'payment_details': TEST_RESPONSE,
            'payment_completed_by': '  test_payment_completed_by  ',
            'payment_completed_by_name': '  test_payment_completed_by_name  ',
        }
        self.test_order = {
            'order_reference': 'test_order_reference',
            'order_type': 'test_order_type',
            'order_started': started_date,
            'order_complete': False,
            'customer_uid': test_customer_uid,
            'user_uid': 'test_user_uid',
            'customer_first_name': 'test_customer_first_name',
            'customer_last_name': 'test_customer_last_name',
            'customer_company_name': 'test_customer_company_name',
            'customer_email': 'test_customer_email',
            'customer_phone': 'test_customer_phone',
            'customer_turnover_ltm': False,
            'customer_tax_number': 'test_customer_tax_number',
            'customer_membership_number': 'test_customer_membership_number',
            'delivery_address_1': 'test_delivery_address_1',
            'delivery_address_2': 'test_delivery_address_2',
            'delivery_city': 'test_delivery_city',
            'delivery_country': 'test_delivery_country',
            'delivery_state': 'test_delivery_state',
            'delivery_post_code': 'test_delivery_post_code',
            'billing_address_1': 'test_billing_address_1',
            'billing_address_2': 'test_billing_address_2',
            'billing_city': 'test_billing_city',
            'billing_country': 'test_billing_country',
            'billing_state': 'test_billing_state',
            'billing_post_code': 'test_billing_post_code',
            'total': 0,
            'currency': 'test_currency',
            'payment_details': TEST_RESPONSE,
            'payment_completed_by': 'test_payment_completed_by',
            'payment_completed_by_name': 'test_payment_completed_by_name',
        }

    def tearDown(self):
        self.testbed.deactivate()

    def _add_test_item_to_basket(self, order):
        order.basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_ONE)

    def test_insert_order(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        self.assertTrue(order_uid)

    def test_get_order(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)

        retrieved_order = koalaecommerce.Orders.get(resource_uid=order_uid)
        self.assertTrue(retrieved_order, u'Stored value mismatch')
        self.assertTrue(retrieved_order.uid, u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_order.created, datetime), u'Stored value mismatch')
        self.assertTrue(isinstance(retrieved_order.updated, datetime), u'Stored value mismatch')
        self.assertEqual(retrieved_order.order_reference, self.test_order['order_reference'], u'Stored order_reference value mismatch')
        self.assertEqual(retrieved_order.order_type, self.test_order['order_type'], u'Stored order_type value mismatch')
        self.assertEqual(retrieved_order.order_status, DEFAULT_ORDER_STATUS, u'Stored order_status value mismatch')
        self.assertEqual(retrieved_order.order_started, self.test_order['order_started'], u'Stored order_started value mismatch')
        self.assertEqual(retrieved_order.order_complete, self.test_order['order_complete'], u'Stored order_status value mismatch')
        self.assertEqual(retrieved_order.customer_uid, self.test_order['customer_uid'], u'Stored customer_uid value mismatch')
        self.assertEqual(retrieved_order.user_uid, self.test_order['user_uid'], u'Stored user_uid value mismatch')
        self.assertEqual(retrieved_order.customer_first_name, self.test_order['customer_first_name'], u'Stored customer_first_name value mismatch')
        self.assertEqual(retrieved_order.customer_last_name, self.test_order['customer_last_name'], u'Stored customer_last_name value mismatch')
        self.assertEqual(retrieved_order.customer_company_name, self.test_order['customer_company_name'], u'Stored customer_company_name value mismatch')
        self.assertEqual(retrieved_order.customer_email, self.test_order['customer_email'], u'Stored customer_email value mismatch')
        self.assertEqual(retrieved_order.customer_phone, self.test_order['customer_phone'], u'Stored customer_phone value mismatch')
        self.assertEqual(retrieved_order.customer_turnover_ltm, self.test_order['customer_turnover_ltm'], u'Stored customer_turnover_ltm value mismatch')
        self.assertEqual(retrieved_order.customer_tax_number, self.test_order['customer_tax_number'], u'Stored customer_tax_number value mismatch')
        self.assertEqual(retrieved_order.customer_membership_number, self.test_order['customer_membership_number'], u'Stored customer_membership_number value mismatch')
        self.assertEqual(retrieved_order.delivery_address_1, self.test_order['delivery_address_1'], u'Stored delivery_address_1 value mismatch')
        self.assertEqual(retrieved_order.delivery_address_2, self.test_order['delivery_address_2'], u'Stored delivery_address_2 value mismatch')
        self.assertEqual(retrieved_order.delivery_city, self.test_order['delivery_city'], u'Stored delivery_city value mismatch')
        self.assertEqual(retrieved_order.delivery_country, self.test_order['delivery_country'], u'Stored delivery_country value mismatch')
        self.assertEqual(retrieved_order.delivery_state, self.test_order['delivery_state'], u'Stored delivery_state value mismatch')
        self.assertEqual(retrieved_order.delivery_post_code, self.test_order['delivery_post_code'], u'Stored delivery_post_code value mismatch')
        self.assertEqual(retrieved_order.billing_address_1, self.test_order['billing_address_1'], u'Stored billing_address_1 value mismatch')
        self.assertEqual(retrieved_order.billing_address_2, self.test_order['billing_address_2'], u'Stored billing_address_2 value mismatch')
        self.assertEqual(retrieved_order.billing_city, self.test_order['billing_city'], u'Stored billing_city value mismatch')
        self.assertEqual(retrieved_order.billing_country, self.test_order['billing_country'], u'Stored billing_country value mismatch')
        self.assertEqual(retrieved_order.billing_state, self.test_order['billing_state'], u'Stored billing_state value mismatch')
        self.assertEqual(retrieved_order.billing_post_code, self.test_order['billing_post_code'], u'Stored billing_post_code value mismatch')
        self.assertEqual(len(retrieved_order.basket), 1, u'Stored basket product count mismatch')
        self.assertEqual(retrieved_order.basket.count(), 1, u'Stored basket item count mismatch')
        self.assertEqual(retrieved_order.total, self.test_order['total'], u'Stored total value mismatch')
        self.assertEqual(retrieved_order.currency, self.test_order['currency'], u'Stored currency value mismatch')
        self.assertEqual(retrieved_order.payment_details, self.test_order['payment_details'], u'Stored payment_details value mismatch')
        self.assertEqual(retrieved_order.payment_completed_by, self.test_order['payment_completed_by'], u'Stored payment_completed_by value mismatch')
        self.assertEqual(retrieved_order.payment_completed_by_name, self.test_order['payment_completed_by_name'], u'Stored payment_completed_by_name value mismatch')

    def test_insert_order_strip_filter(self):
        order = koalaecommerce.Orders.new(**self.test_order_with_spaces)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)

        retrieved_order = koalaecommerce.Orders.get(resource_uid=order_uid)

        self.assertEqual(retrieved_order.order_reference, self.test_order['order_reference'], u'Stored order_reference value mismatch')
        self.assertEqual(retrieved_order.order_type, self.test_order['order_type'], u'Stored order_type value mismatch')
        self.assertEqual(retrieved_order.order_status, DEFAULT_ORDER_STATUS, u'Stored order_status value mismatch')
        self.assertEqual(retrieved_order.order_started, self.test_order['order_started'], u'Stored order_started value mismatch')
        self.assertEqual(retrieved_order.order_complete, self.test_order['order_complete'], u'Stored order_status value mismatch')
        self.assertEqual(retrieved_order.customer_uid, self.test_order['customer_uid'], u'Stored customer_uid value mismatch')
        self.assertEqual(retrieved_order.user_uid, self.test_order['user_uid'], u'Stored user_uid value mismatch')
        self.assertEqual(retrieved_order.customer_first_name, self.test_order['customer_first_name'], u'Stored customer_first_name value mismatch')
        self.assertEqual(retrieved_order.customer_last_name, self.test_order['customer_last_name'], u'Stored customer_last_name value mismatch')
        self.assertEqual(retrieved_order.customer_company_name, self.test_order['customer_company_name'], u'Stored customer_company_name value mismatch')
        self.assertEqual(retrieved_order.customer_email, self.test_order['customer_email'], u'Stored customer_email value mismatch')
        self.assertEqual(retrieved_order.customer_phone, self.test_order['customer_phone'], u'Stored customer_phone value mismatch')
        self.assertEqual(retrieved_order.customer_turnover_ltm, self.test_order['customer_turnover_ltm'], u'Stored customer_turnover_ltm value mismatch')
        self.assertEqual(retrieved_order.customer_tax_number, self.test_order['customer_tax_number'], u'Stored customer_tax_number value mismatch')
        self.assertEqual(retrieved_order.customer_membership_number, self.test_order['customer_membership_number'], u'Stored customer_membership_number value mismatch')
        self.assertEqual(retrieved_order.delivery_address_1, self.test_order['delivery_address_1'], u'Stored delivery_address_1 value mismatch')
        self.assertEqual(retrieved_order.delivery_address_2, self.test_order['delivery_address_2'], u'Stored delivery_address_2 value mismatch')
        self.assertEqual(retrieved_order.delivery_city, self.test_order['delivery_city'], u'Stored delivery_city value mismatch')
        self.assertEqual(retrieved_order.delivery_country, self.test_order['delivery_country'], u'Stored delivery_country value mismatch')
        self.assertEqual(retrieved_order.delivery_state, self.test_order['delivery_state'], u'Stored delivery_state value mismatch')
        self.assertEqual(retrieved_order.delivery_post_code, self.test_order['delivery_post_code'], u'Stored delivery_post_code value mismatch')
        self.assertEqual(retrieved_order.billing_address_1, self.test_order['billing_address_1'], u'Stored billing_address_1 value mismatch')
        self.assertEqual(retrieved_order.billing_address_2, self.test_order['billing_address_2'], u'Stored billing_address_2 value mismatch')
        self.assertEqual(retrieved_order.billing_city, self.test_order['billing_city'], u'Stored billing_city value mismatch')
        self.assertEqual(retrieved_order.billing_country, self.test_order['billing_country'], u'Stored billing_country value mismatch')
        self.assertEqual(retrieved_order.billing_state, self.test_order['billing_state'], u'Stored billing_state value mismatch')
        self.assertEqual(retrieved_order.billing_post_code, self.test_order['billing_post_code'], u'Stored billing_post_code value mismatch')
        self.assertEqual(len(retrieved_order.basket), 1, u'Stored basket product count mismatch')
        self.assertEqual(retrieved_order.basket.count(), 1, u'Stored basket item count mismatch')
        self.assertEqual(retrieved_order.total, self.test_order['total'], u'Stored total value mismatch')
        self.assertEqual(retrieved_order.currency, self.test_order['currency'], u'Stored currency value mismatch')
        self.assertEqual(retrieved_order.payment_details, self.test_order['payment_details'], u'Stored payment_details value mismatch')
        self.assertEqual(retrieved_order.payment_completed_by, self.test_order['payment_completed_by'], u'Stored payment_completed_by value mismatch')
        self.assertEqual(retrieved_order.payment_completed_by_name, self.test_order['payment_completed_by_name'], u'Stored payment_completed_by_name value mismatch')

    def test_update_order(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        retrieved_order = koalaecommerce.Orders.get(resource_uid=order_uid)

        retrieved_order.order_type = 'updated_order_type'
        retrieved_order.order_status = 'PAID'
        retrieved_order.user_uid = 'updated_user_uid'
        retrieved_order.customer_first_name = 'updated_customer_first_name'
        retrieved_order.customer_last_name = 'updated_customer_last_name'
        retrieved_order.customer_company_name = 'updated_customer_company_name'
        retrieved_order.customer_email = 'updated_customer_email'
        retrieved_order.customer_phone = 'updated_customer_phone'
        retrieved_order.customer_turnover_ltm = True
        retrieved_order.customer_tax_number = 'updated_customer_tax_number'
        retrieved_order.customer_membership_number = 'updated_customer_membership_number'
        retrieved_order.delivery_address_1 = 'updated_delivery_address_1'
        retrieved_order.delivery_address_2 = 'updated_delivery_address_2'
        retrieved_order.delivery_city = 'updated_delivery_city'
        retrieved_order.delivery_country = 'updated_delivery_country'
        retrieved_order.delivery_state = 'updated_delivery_state'
        retrieved_order.delivery_post_code = 'updated_delivery_post_code'
        retrieved_order.billing_address_1 = 'updated_billing_address_1'
        retrieved_order.billing_address_2 = 'updated_billing_address_2'
        retrieved_order.billing_city = 'updated_billing_city'
        retrieved_order.billing_country = 'updated_billing_country'
        retrieved_order.billing_state = 'updated_billing_state'
        retrieved_order.billing_post_code = 'updated_billing_post_code'
        retrieved_order.total = 100
        retrieved_order.currency = 'updated_currency'
        retrieved_order.payment_details = TEST_RESPONSE_2
        retrieved_order.payment_completed_by = 'updated_payment_completed_by'
        retrieved_order.payment_completed_by_name = 'updated_payment_completed_by_name'

        retrieved_order.basket.add(product=NORMAL_ITEM_1, customisation=EXAMPLE_CUSTOMISATION_TWO)

        koalaecommerce.Orders.update(resource_object=retrieved_order)
        updated_order = koalaecommerce.Orders.get(resource_uid=order_uid)

        self.assertEqual(retrieved_order.uid, updated_order.uid, u'UID mismatch')
        self.assertEqual(retrieved_order.created, updated_order.created, u'Created date has changed')
        self.assertNotEqual(retrieved_order.updated, updated_order.updated, u'Updated date not changed')
        self.assertEqual(updated_order.order_reference, retrieved_order.order_reference, u'Stored order_reference value mismatch')
        self.assertEqual(updated_order.order_type, 'updated_order_type', u'Stored order_type value mismatch')
        self.assertEqual(updated_order.order_status, 'PAID', u'Stored order_status value mismatch')
        self.assertEqual(updated_order.order_started, retrieved_order.order_started, u'Stored order_started value mismatch')
        self.assertEqual(updated_order.order_complete, False, u'Stored order_complete value mismatch')
        self.assertEqual(updated_order.customer_uid, self.test_order['customer_uid'], u'Stored customer_uid value mismatch')
        self.assertEqual(updated_order.user_uid, 'updated_user_uid', u'Stored user_uid value mismatch')
        self.assertEqual(updated_order.customer_first_name, 'updated_customer_first_name', u'Stored customer_first_name value mismatch')
        self.assertEqual(updated_order.customer_last_name, 'updated_customer_last_name', u'Stored customer_last_name value mismatch')
        self.assertEqual(updated_order.customer_company_name, 'updated_customer_company_name', u'Stored customer_company_name value mismatch')
        self.assertEqual(updated_order.customer_email, 'updated_customer_email', u'Stored customer_email value mismatch')
        self.assertEqual(updated_order.customer_phone, 'updated_customer_phone', u'Stored customer_phone value mismatch')
        self.assertEqual(updated_order.customer_turnover_ltm, True, u'Stored customer_turnover_ltm value mismatch')
        self.assertEqual(updated_order.customer_tax_number, 'updated_customer_tax_number', u'Stored customer_tax_number value mismatch')
        self.assertEqual(updated_order.customer_membership_number, 'updated_customer_membership_number', u'Stored customer_membership_number value mismatch')
        self.assertEqual(updated_order.delivery_address_1, 'updated_delivery_address_1', u'Stored delivery_address_1 value mismatch')
        self.assertEqual(updated_order.delivery_address_2, 'updated_delivery_address_2', u'Stored delivery_address_2 value mismatch')
        self.assertEqual(updated_order.delivery_city, 'updated_delivery_city', u'Stored delivery_city value mismatch')
        self.assertEqual(updated_order.delivery_country, 'updated_delivery_country', u'Stored delivery_country value mismatch')
        self.assertEqual(updated_order.delivery_state, 'updated_delivery_state', u'Stored delivery_state value mismatch')
        self.assertEqual(updated_order.delivery_post_code, 'updated_delivery_post_code', u'Stored delivery_post_code value mismatch')
        self.assertEqual(updated_order.billing_address_1, 'updated_billing_address_1', u'Stored billing_address_1 value mismatch')
        self.assertEqual(updated_order.billing_address_2, 'updated_billing_address_2', u'Stored billing_address_2 value mismatch')
        self.assertEqual(updated_order.billing_city, 'updated_billing_city', u'Stored billing_city value mismatch')
        self.assertEqual(updated_order.billing_country, 'updated_billing_country', u'Stored billing_country value mismatch')
        self.assertEqual(updated_order.billing_state, 'updated_billing_state', u'Stored billing_state value mismatch')
        self.assertEqual(updated_order.billing_post_code, 'updated_billing_post_code', u'Stored billing_post_code value mismatch')
        self.assertEqual(len(updated_order.basket), 1, u'Stored basket product count mismatch')
        self.assertEqual(updated_order.basket.count(), 2, u'Stored basket item count mismatch')
        self.assertEqual(updated_order.total, 100, u'Stored total value mismatch')
        self.assertEqual(updated_order.currency, 'updated_currency', u'Stored currency value mismatch')
        self.assertEqual(updated_order.payment_details, TEST_RESPONSE_2, u'Stored payment_details value mismatch')
        self.assertEqual(updated_order.payment_completed_by, 'updated_payment_completed_by', u'Stored payment_completed_by value mismatch')
        self.assertEqual(updated_order.payment_completed_by_name, 'updated_payment_completed_by_name', u'Stored payment_completed_by_name value mismatch')

    def test_delete_order(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        koalaecommerce.Orders.delete(resource_uid=order_uid)
        retrieved_order = koalaecommerce.Orders.get(resource_uid=order_uid)
        self.assertFalse(retrieved_order)

    def test_insert_search(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        koalaecommerce.Orders.insert(resource_object=order)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Deferred task missing')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        search_result = koalaecommerce.Orders.search(
            query_string='customer_company_name: {}'.format(self.test_order['customer_company_name']))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_update_search(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        retrieved_order = koalaecommerce.Orders.get(resource_uid=order_uid)
        retrieved_order.customer_company_name = 'updated_customer_company_name'
        koalaecommerce.Orders.update(resource_object=retrieved_order)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaecommerce.Orders.search(query_string='customer_company_name: {}'.format('updated_customer_company_name'))
        self.assertEqual(search_result.results_count, 1, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 1, u'Query returned incorrect number of results')

    def test_delete_search(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 1, u'Invalid number of Deferred tasks')

        deferred.run(tasks[0].payload)  # Doesn't return anything so nothing to test

        koalaecommerce.Orders.delete(resource_uid=order_uid)

        tasks = self.task_queue.get_filtered_tasks()
        self.assertEqual(len(tasks), 2, u'Invalid number of Deferred tasks')

        deferred.run(tasks[1].payload)  # Doesn't return anything so nothing to test

        search_result = koalaecommerce.Orders.search(
            query_string='customer_company_name: {}'.format(self.test_order['customer_company_name']))
        self.assertEqual(search_result.results_count, 0, u'Query returned incorrect count')
        self.assertEqual(len(search_result.results), 0, u'Query returned incorrect number of results')

    def test_get_customer_order(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)

        orders = koalaecommerce.Orders.get_by_customer_uid(customer_uid=self.test_order['customer_uid'])
        self.assertEqual(len(orders), 1, u'Query returned incorrect number of orders')
        self.assertEqual(orders[0].customer_uid, self.test_order['customer_uid'], u'Query returned incorrect number of orders')

    def test_get_customer_order_with_type(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        self._add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)

        orders = koalaecommerce.Orders.get_by_customer_uid(customer_uid=self.test_order['customer_uid'], order_type=self.test_order['order_type'])
        self.assertEqual(len(orders), 1, u'Query returned incorrect number of orders')
        self.assertEqual(orders[0].customer_uid, self.test_order['customer_uid'], u'Query returned incorrect number of orders')

    def _build_complete_order(self):
        order = koalaecommerce.Orders.new(**self.test_order)
        _add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        order = koalaecommerce.Orders.get(resource_uid=order_uid)

        payment_response = PaymentGatewayResponse(gateway_transaction_uid='test_txuid',
                                                  order_reference=order.order_reference,
                                                  order_uid=order_uid,
                                                  success=True,
                                                  amount=69,
                                                  timestamp=datetime.now(),
                                                  method='SagePay',
                                                  encoded_response='encoded_response')

        koalaecommerce.Orders.complete_order(payment_response=payment_response,
                                             completed_by_uid='test_uid',
                                             completed_by_name='Test User')

        return koalaecommerce.Orders.get(resource_uid=order_uid)

    def test_complete_order(self):
        completed_order = self._build_complete_order()
        self.assertTrue(completed_order.order_complete,  u'order_complete mismatch')
        self.assertEqual(completed_order.order_status, 'PAID', u'order_status mismatch')
        self.assertEqual(completed_order.payment_completed_by, 'test_uid', u'payment_completed_by mismatch')
        self.assertEqual(completed_order.payment_completed_by_name, 'Test User', u'payment_completed_by_name mismatch')

    def test_get_customer_order_completed(self):
        completed_order = self._build_complete_order()
        orders = koalaecommerce.Orders.get_by_customer_uid(customer_uid=self.test_order['customer_uid'],
                                                           order_complete=True)
        self.assertEqual(len(orders), 1, u'Query returned incorrect number of orders')
        self.assertEqual(orders[0].customer_uid, self.test_order['customer_uid'], u'Query returned incorrect order')

    def test_get_customer_order_with_type_and_completed(self):
        completed_order = self._build_complete_order()
        orders = koalaecommerce.Orders.get_by_customer_uid(customer_uid=self.test_order['customer_uid'],
                                                           order_complete=True,
                                                           order_type=self.test_order['order_type'])
        self.assertEqual(len(orders), 1, u'Query returned incorrect number of orders')
        self.assertEqual(orders[0].customer_uid, self.test_order['customer_uid'], u'Query returned incorrect order')

    def test_completed_order_block_insert(self):
        order = koalaecommerce.Orders.new(**self.test_order)

        order.order_complete = True
        with self.assertRaises(ValueError):
            koalaecommerce.Orders.insert(resource_object=order)

    def test_completed_order_block_update(self):
        completed_order = self._build_complete_order()

        completed_order.billing_address_1 = 'Test modification'
        with self.assertRaises(ValueError):
            koalaecommerce.Orders.update(resource_object=completed_order)

    def test_completed_order_block_delete(self):
        completed_order = self._build_complete_order()

        with self.assertRaises(ValueError):
            koalaecommerce.Orders.delete(resource_uid=completed_order.uid)

    def test_order_reference_generator(self):
        # TODO: make sure the reference changes is not completed byb not if completed.
        pass


class TestSagePayGatewayRequest(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        self.valid_test_order = VALID_UK_ORDER

        self.invalid_test_order = INVALID_ORDER

        self.gateway_config = {
            'payment_gateway': 'sagepay',
            'merchant_info': MERCHANT_INFO,
            'endpoint_url': 'https://test.sagepay.com/gateway/service/vspform-register.vsp',
            'success_url': 'http://localhost:8081/payments/sagepay/success?request_signature={request_signature}',
            'failure_url': 'http://localhost:8081/payments/sagepay/failure?request_signature={request_signature}',
            'basket_type': 'simple',
            'encryption_key': '170ankOS9Rd4XA8n',
            'encryption_iv': '170ankOS9Rd4XA8n',
            'vendor': 'testvendorid',
            'request_signing_key': REQUEST_SIGNING_KEY,
            'response_signing_key': RESPONSE_SIGNING_KEY,
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_empty_basket_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

    def test_missing_order_details_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.invalid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

    def test_missing_gateway_config_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=None)

    def test_request_object_default_properties(self):
        order = koalaecommerce.Orders.new(**self.valid_test_order)
        _add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        order = koalaecommerce.Orders.get(resource_uid=order_uid)

        signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

        self.assertEqual(payment_request.title, 'SagePay', u'Payment title mismatch')
        self.assertEqual(payment_request.vendor, self.gateway_config['vendor'], u'Payment vendor mismatch')
        self.assertEqual(payment_request.vpsprotocol, 3.00, u'Payment vpsprotocol mismatch')
        self.assertEqual(payment_request.txtype, 'PAYMENT', u'Payment txtype mismatch')
        self.assertEqual(payment_request.endpoint, self.gateway_config['endpoint_url'], u'Payment endpoint mismatch')
        self.assertTrue(payment_request.crypt.startswith('@'), u'Payment encrypted_payload invalid')

    def test_request_object_crypt_properties(self):
        pass


class TestBACSGatewayRequest(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        self.valid_test_order = VALID_UK_ORDER

        self.invalid_test_order = INVALID_ORDER

        self.gateway_config = {
            'payment_gateway': 'bacs',
            'merchant_info': MERCHANT_INFO,
            'endpoint_url': 'http://localhost:8081/payments/bacs/process',
            'success_url': 'http://localhost:8081/payments/bacs/success?request_signature={request_signature}',
            'failure_url': 'http://localhost:8081/payments/bacs/failure?request_signature={request_signature}',
            'encryption_key': '170ankOS9Rd4XA8n',
            'encryption_iv': '170ankOS9Rd4XA8n',
            'vendor': 'testvendorid',
            'request_signing_key': REQUEST_SIGNING_KEY,
            'response_signing_key': RESPONSE_SIGNING_KEY,
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_empty_basket_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

    def test_missing_order_details_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.invalid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

    def test_missing_gateway_config_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=None)

    def test_request_object_default_properties(self):
        order = koalaecommerce.Orders.new(**self.valid_test_order)
        _add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        order = koalaecommerce.Orders.get(resource_uid=order_uid)

        signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

        self.assertEqual(payment_request.title, 'BACS', u'Payment title mismatch')
        self.assertEqual(payment_request.vendor, self.gateway_config['vendor'], u'Payment vendor mismatch')
        self.assertEqual(payment_request.endpoint, self.gateway_config['endpoint_url'], u'Payment endpoint mismatch')
        self.assertTrue(payment_request.encrypted_payload.startswith('@'), u'Payment encrypted_payload invalid')

    def test_request_object_crypt_properties(self):
        pass


class TestChequeGatewayRequest(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        self.valid_test_order = VALID_UK_ORDER

        self.invalid_test_order = INVALID_ORDER

        self.gateway_config = {
            'payment_gateway': 'cheque',
            'merchant_info': MERCHANT_INFO,
            'endpoint_url': 'http://localhost:8081/payments/cheque/process',
            'success_url': 'http://localhost:8081/payments/cheque/success?request_signature={request_signature}',
            'failure_url': 'http://localhost:8081/payments/cheque/failure?request_signature={request_signature}',
            'encryption_key': '170ankOS9Rd4XA8n',
            'encryption_iv': '170ankOS9Rd4XA8n',
            'vendor': 'testvendorid',
            'request_signing_key': REQUEST_SIGNING_KEY,
            'response_signing_key': RESPONSE_SIGNING_KEY,
        }

    def tearDown(self):
        self.testbed.deactivate()

    def test_empty_basket_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

    def test_missing_order_details_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.invalid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

    def test_missing_gateway_config_fails_request(self):
        with self.assertRaises(ValueError):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=None)

    def test_request_object_default_properties(self):
        order = koalaecommerce.Orders.new(**self.valid_test_order)
        _add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        order = koalaecommerce.Orders.get(resource_uid=order_uid)

        signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config)

        self.assertEqual(payment_request.title, 'Cheque', u'Payment title mismatch')
        self.assertEqual(payment_request.vendor, self.gateway_config['vendor'], u'Payment vendor mismatch')
        self.assertEqual(payment_request.endpoint, self.gateway_config['endpoint_url'], u'Payment endpoint mismatch')
        self.assertTrue(payment_request.encrypted_payload.startswith('@'), u'Payment encrypted_payload invalid')

    def test_request_object_crypt_properties(self):
        pass


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Remaining setup needed for test cases
        self.valid_test_order = VALID_UK_ORDER
        self.invalid_test_order = INVALID_ORDER

    def tearDown(self):
        self.testbed.deactivate()

    def test_analytics_server(self):
        order = koalaecommerce.Orders.new(**self.valid_test_order)
        _add_test_item_to_basket(order=order)
        order_uid = koalaecommerce.Orders.insert(resource_object=order)
        order = koalaecommerce.Orders.get(resource_uid=order_uid)

        response, item_responses = self.order_to_google_analytics(order=order)
        self.assertEqual(response, 200, u'Incorrect status')

    def order_to_google_analytics(self, order):
        """ Posts an Event Tracking message to Google Analytics. """
        order_uuid = uuid.uuid4()
        total = order.basket.get_total()
        gross = float(total.gross)
        tax = float(total.gross - total.net)
        transaction_fields = {
            "v": "1",  # Version.
            "an": "Koala Ecommerce",
            "tid": 'UA-69007156-1',  # Tracking ID / Web property / Property ID.
            "cid": order_uuid,  # Anonymous Client ID.
            "t": "transaction",  # Event hit type.
            "ti": order.order_reference,
            "ta": order.customer_company_name,
            "tr": gross,
            "ts": 0.00,
            "tt": tax,
            "cu": 'GBP',
        }
        form_data = urllib.urlencode(transaction_fields)
        result = urlfetch.fetch(url="http://www.google-analytics.com/collect",
                                payload=form_data,
                                method=urlfetch.POST,
                                headers={"Content-Type": "application/x-www-form-urlencoded"})

        item_responses = []
        for product_index, product in enumerate(order.basket):
            item_fields = {
                "v": "1",  # Version.
                "an": "Koala Ecommerce",
                "tid": 'UA-69007156-1',  # Tracking ID / Web property / Property ID.
                "cid": order_uuid,  # Anonymous Client ID.
                "t": "item",  # Event hit type.
                "ti": order.order_reference,
                "in": '{} Entry'.format(order.order_type),
                "ip": float(product.product.get_price().net),
                "iq": product.get_quantity(),
                "ic": product.product.sku,
                "iv": product.product.sku,
                "cu": 'GBP',
            }
            form_data = urllib.urlencode(item_fields)
            result = urlfetch.fetch(url="http://www.google-analytics.com/collect",
                                    payload=form_data,
                                    method=urlfetch.POST,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"})
            item_responses.append(result.status_code)

        return result.status_code, item_responses

if ALLOW_BROWSER_TESTING:
    # In order to run these tests you must supply the sagepay config and install splinter, chromedriver and paste.
    import os
    import time
    import requests
    import subprocess
    import urlparse
    from splinter import Browser
    from koalaemailrenderer import EmailRenderer
    from koalasendgrid import send_email

    def expiry_date(years=1):
        """Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).
        :param years:

        From: http://stackoverflow.com/a/15743908
        """
        today = datetime.now()
        try:
            expires = today.replace(year=today.year + years)
        except ValueError:
            expires = today + (date(today.year + years, 1, 1) - date(today.year, 1, 1))

        return expires.strftime('%m'), expires.strftime('%y')


    APP_INFO = {
        'app_name': config.settings.get('app_name'),
        'title': config.settings.get('title'),
        'url': config.settings.get('url'),
        'copyright': config.settings.get('copyright'),
        'support_email': config.settings.get('support_email'),
        'support_url': config.settings.get('support_url'),
    }

    GLOBAL_RENDERER_VARS = {
        'app_info': APP_INFO,
    }

    JINJA2_ENGINE_CONFIG = {
        'environment_args': {'extensions': config.settings.getlist('jinja2_extensions'),
                             'autoescape': config.settings.getboolean('jinja2_env_autoescape')},
        'theme_base_template_path': config.settings.getlist('email_template_base_path'),
        'theme_compiled_path': config.settings.get('email_template_compiled_path'),
        'enable_i18n': config.settings.getboolean('jinja2_enable_i18n'),
    }

    RENDERER_CONFIG = {
        'jinja2_engine_config': JINJA2_ENGINE_CONFIG,
        'global_renderer_vars': GLOBAL_RENDERER_VARS,
    }

    ORDER_CONFIRMATION_EMAIL_TEMPLATE = config.settings.get('order_confirmation_email_template')


    # class TestSagePayServer(unittest.TestCase):
    #     def setUp(self):
    #         # First, create an instance of the Testbed class.
    #         self.testbed = testbed.Testbed()
    #         # Then activate the testbed, which prepares the service stubs for use.
    #         self.testbed.activate()
    #         # Next, declare which service stubs you want to use.
    #         self.testbed.init_datastore_v3_stub()
    #         self.testbed.init_memcache_stub()
    #         self.testbed.init_search_stub()
    #         self.testbed.init_taskqueue_stub(root_path='.')
    #         self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
    #         # Remaining setup needed for test cases
    #         self.test_card_details = {
    #             'visa_3d_secure': '4929 0000 0000 6',
    #             'visa': '4929 0000 0555 9',
    #         }
    #         self.test_card_cvc = '123'
    #         self.test_card_expires_mm, self.test_card_expires_yy = expiry_date()
    #
    #         self.valid_test_order = VALID_UK_ORDER
    #         self.invalid_test_order = INVALID_ORDER
    #
    #         self.gateway_config = {
    #             'payment_gateway': 'sagepay',
    #             'merchant_info': MERCHANT_INFO,
    #             'endpoint_url': config.secrets.get('sagepay_test_endpoint'),
    #             'success_url': 'http://127.0.0.1:8080/payments/sagepay/success/callback?request_signature={request_signature}',
    #             'failure_url': 'http://127.0.0.1:8080/payments/sagepay/failure/callback?request_signature={request_signature}',
    #             'basket_type': 'simple',
    #             'encryption_key': config.secrets.get('sagepay_vendor_key'),
    #             'encryption_iv': config.secrets.get('sagepay_vendor_key'),
    #             'vendor': config.secrets.get('sagepay_vendor'),
    #             'request_signing_key': REQUEST_SIGNING_KEY,
    #             'response_signing_key': RESPONSE_SIGNING_KEY,
    #         }
    #         dirname, filename = os.path.split(os.path.abspath(__file__))
    #         self.server = subprocess.Popen(['python', dirname + '/test_server.py'])
    #         time.sleep(1)   # Need to wait for the server to initialize. There are probably better ways...
    #
    #     def tearDown(self):
    #         self.testbed.deactivate()
    #         self.server.kill()
    #
    #     def test_server(self):
    #         card_name = 'VISA'
    #         card_type = 'visa'
    #
    #         order = koalaecommerce.Orders.new(**self.valid_test_order)
    #         _add_test_item_to_basket(order=order)
    #         order_uid = koalaecommerce.Orders.insert(resource_object=order)
    #         order = koalaecommerce.Orders.get(resource_uid=order_uid)
    #
    #         additional_signature_values = {
    #             'company_uid': TEST_CUSTOMER_UID,
    #         }
    #
    #         signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config, additional_signature_kwargs=additional_signature_values)
    #
    #         update_response = requests.post('http://127.0.0.1:8080/update', data=payment_request.__dict__)
    #         self.assertEqual(update_response.status_code, 200, u'Error "{}" while updating'.format(update_response.status_code))
    #
    #         with Browser('chrome', executable_path=config.secrets.get('chromedriver_path')) as browser:
    #             browser.visit('http://127.0.0.1:8080/pay')
    #             browser.find_by_id('pay').first.click()
    #             browser.find_by_value(card_name).first.click()
    #             browser.find_by_id('form-card_details.field-pan').fill(self.test_card_details[card_type])
    #             browser.find_by_id('form-card_details.field-expiry_mm').fill(self.test_card_expires_mm)
    #             browser.find_by_id('form-card_details.field-expiry_yy').fill(self.test_card_expires_yy)
    #             browser.find_by_id('form-card_details.field-cvc').fill(self.test_card_cvc)
    #             browser.find_by_value('proceed').first.click()
    #             browser.find_by_value('proceed').first.click()
    #             # Sometimes the test runs too fast for the browser and the sagepay response is not saved. Crude check
    #             # cycle that works most of the time. The wait_time arg seems to always fail.
    #             found = False
    #             while not found:
    #                 found = browser.is_text_present('response:')
    #                 time.sleep(2)
    #
    #         result = requests.get('http://127.0.0.1:8080/result')
    #         self.assertEqual(result.status_code, 200, u'Error "{}" while fetching result'.format(result.status_code))
    #         result_parts = result.content.split(':')
    #         self.assertEqual(len(result_parts), 3, u'Result incorrectly formatted')
    #         self.assertEqual(result_parts[0], 'response', u'Result incorrectly formatted')
    #         self.assertEqual(result_parts[1], 'Success', u'Result incorrectly formatted')
    #         response_params = dict(urlparse.parse_qsl(result_parts[2]))
    #
    #         response, decrypted_signature = koalaecommerce.Payments.verify_response(
    #             request_signature=response_params['request_signature'],
    #             gateway_response=response_params['crypt'],
    #             payment_config=self.gateway_config,
    #         )
    #
    #         self.assertTrue(response.success, u'Gateway response should be successful')
    #
    #         updated_order_uid = koalaecommerce.Orders.complete_order(payment_response=response,
    #                                                                  completed_by_uid='Example_UID',
    #                                                                  completed_by_name='Test User')
    #
    #         self.assertTrue(updated_order_uid, u'Order not completed')
    #
    #         EmailRenderer.configure(configuration=RENDERER_CONFIG)
    #
    #         email_template_vars = {
    #             'order': order
    #         }
    #
    #         send_email_kwargs = {
    #             'to_address': order.customer_email,
    #             'subject': u'Thank you for your order',
    #             'to_name': u'{0} {1}'.format(order.customer_first_name, order.customer_last_name),
    #             'body': EmailRenderer.render(template_path=ORDER_CONFIRMATION_EMAIL_TEMPLATE, template_vars=email_template_vars)
    #         }
    #
    #         response_code, response_message = send_email(**send_email_kwargs)
    #
    #         self.assertEqual(response_code, 200, u'Error "{}" while emailing confirmation'.format(response_code))



            # Need to visit /pay in browser and then select 'pay' button to initiate SagePay transaction.
            # Annoyingly we can't just use the requests library for this as JS execution is mandatory on SagePay


    class TestBACSServer(unittest.TestCase):
        def setUp(self):
            # First, create an instance of the Testbed class.
            self.testbed = testbed.Testbed()
            # Then activate the testbed, which prepares the service stubs for use.
            self.testbed.activate()
            # Next, declare which service stubs you want to use.
            self.testbed.init_datastore_v3_stub()
            self.testbed.init_memcache_stub()
            self.testbed.init_search_stub()
            self.testbed.init_taskqueue_stub(root_path='.')
            self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
            # Remaining setup needed for test cases

            self.valid_test_order = VALID_UK_ORDER
            self.invalid_test_order = INVALID_ORDER

            self.gateway_config = {
                'payment_gateway': 'bacs',
                'merchant_info': MERCHANT_INFO,
                'endpoint_url': 'http://127.0.0.1:8080/offlinepayment/bacs',
                'success_url': 'http://127.0.0.1:8080/payments/offline/success/callback?request_signature={request_signature}',
                'failure_url': 'http://127.0.0.1:8080/payments/offline/failure/callback?request_signature={request_signature}',
                'basket_type': 'simple',
                'encryption_key': config.secrets.get('sagepay_vendor_key'),
                'encryption_iv': config.secrets.get('sagepay_vendor_key'),
                'vendor': config.secrets.get('sagepay_vendor'),
                'request_signing_key': REQUEST_SIGNING_KEY,
                'response_signing_key': RESPONSE_SIGNING_KEY,
            }
            dirname, filename = os.path.split(os.path.abspath(__file__))
            self.server = subprocess.Popen(['python', dirname + '/test_server.py'])
            time.sleep(2)   # Need to wait for the server to initialize. There are probably better ways...

        def tearDown(self):
            self.testbed.deactivate()
            self.server.kill()

        def test_server(self):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            additional_signature_values = {
                'company_uid': TEST_CUSTOMER_UID,
            }

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config, additional_signature_kwargs=additional_signature_values)

            update_response = requests.post('http://127.0.0.1:8080/update/offline', data=payment_request.__dict__)
            self.assertEqual(update_response.status_code, 200, u'Error "{}" while updating'.format(update_response.status_code))

            with Browser('chrome', executable_path=config.secrets.get('chromedriver_path')) as browser:
                browser.visit('http://127.0.0.1:8080/pay/offline')
                browser.find_by_id('pay').first.click()
                # Sometimes the test runs too fast for the browser and the sagepay response is not saved. Crude check
                # cycle that works most of the time. The wait_time arg seems to always fail.
                found = False
                while not found:
                    found = browser.is_text_present('response:')
                    time.sleep(2)

            result = requests.get('http://127.0.0.1:8080/result/offline')
            self.assertEqual(result.status_code, 200, u'Error "{}" while fetching result'.format(result.status_code))
            result_parts = result.content.split(':')
            self.assertEqual(len(result_parts), 3, u'Result incorrectly formatted')
            self.assertEqual(result_parts[0], 'response', u'Result incorrectly formatted')
            self.assertEqual(result_parts[1], 'Success', u'Result incorrectly formatted')
            response_params = dict(urlparse.parse_qsl(result_parts[2]))

            response, decrypted_signature = koalaecommerce.Payments.verify_response(
                request_signature=response_params['request_signature'],
                gateway_response=response_params['encrypted_payload'],
                payment_config=self.gateway_config,
            )

            self.assertTrue(response.success, u'Gateway response should be successful')

            updated_order_uid = koalaecommerce.Orders.complete_order(payment_response=response,
                                                                     completed_by_uid='Example_UID',
                                                                     completed_by_name='Test User')

            self.assertTrue(updated_order_uid, u'Order not completed')


    class TestChequeServer(unittest.TestCase):
        def setUp(self):
            # First, create an instance of the Testbed class.
            self.testbed = testbed.Testbed()
            # Then activate the testbed, which prepares the service stubs for use.
            self.testbed.activate()
            # Next, declare which service stubs you want to use.
            self.testbed.init_datastore_v3_stub()
            self.testbed.init_memcache_stub()
            self.testbed.init_search_stub()
            self.testbed.init_taskqueue_stub(root_path='.')
            self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
            # Remaining setup needed for test cases

            self.valid_test_order = VALID_UK_ORDER
            self.invalid_test_order = INVALID_ORDER

            self.gateway_config = {
                'payment_gateway': 'cheque',
                'merchant_info': MERCHANT_INFO,
                'endpoint_url': 'http://127.0.0.1:8080/offlinepayment/cheque',
                'success_url': 'http://127.0.0.1:8080/payments/offline/success/callback?request_signature={request_signature}',
                'failure_url': 'http://127.0.0.1:8080/payments/offline/failure/callback?request_signature={request_signature}',
                'basket_type': 'simple',
                'encryption_key': config.secrets.get('sagepay_vendor_key'),
                'encryption_iv': config.secrets.get('sagepay_vendor_key'),
                'vendor': config.secrets.get('sagepay_vendor'),
                'request_signing_key': REQUEST_SIGNING_KEY,
                'response_signing_key': RESPONSE_SIGNING_KEY,
            }
            dirname, filename = os.path.split(os.path.abspath(__file__))
            self.server = subprocess.Popen(['python', dirname + '/test_server.py'])
            time.sleep(2)   # Need to wait for the server to initialize. There are probably better ways...

        def tearDown(self):
            self.testbed.deactivate()
            self.server.kill()

        def test_server(self):
            order = koalaecommerce.Orders.new(**self.valid_test_order)
            _add_test_item_to_basket(order=order)
            order_uid = koalaecommerce.Orders.insert(resource_object=order)
            order = koalaecommerce.Orders.get(resource_uid=order_uid)

            additional_signature_values = {
                'company_uid': TEST_CUSTOMER_UID,
            }

            signature, payment_request = koalaecommerce.Payments.new(order=order, payment_config=self.gateway_config, additional_signature_kwargs=additional_signature_values)

            update_response = requests.post('http://127.0.0.1:8080/update/offline', data=payment_request.__dict__)
            self.assertEqual(update_response.status_code, 200, u'Error "{}" while updating'.format(update_response.status_code))

            with Browser('chrome', executable_path=config.secrets.get('chromedriver_path')) as browser:
                browser.visit('http://127.0.0.1:8080/pay/offline')
                browser.find_by_id('pay').first.click()
                # Sometimes the test runs too fast for the browser and the sagepay response is not saved. Crude check
                # cycle that works most of the time. The wait_time arg seems to always fail.
                found = False
                while not found:
                    found = browser.is_text_present('response:')
                    time.sleep(2)

            result = requests.get('http://127.0.0.1:8080/result/offline')
            self.assertEqual(result.status_code, 200, u'Error "{}" while fetching result'.format(result.status_code))
            result_parts = result.content.split(':')
            self.assertEqual(len(result_parts), 3, u'Result incorrectly formatted')
            self.assertEqual(result_parts[0], 'response', u'Result incorrectly formatted')
            self.assertEqual(result_parts[1], 'Success', u'Result incorrectly formatted')
            response_params = dict(urlparse.parse_qsl(result_parts[2]))

            response, decrypted_signature = koalaecommerce.Payments.verify_response(
                request_signature=response_params['request_signature'],
                gateway_response=response_params['encrypted_payload'],
                payment_config=self.gateway_config,
            )

            self.assertTrue(response.success, u'Gateway response should be successful')

            updated_order_uid = koalaecommerce.Orders.complete_order(payment_response=response,
                                                                     completed_by_uid='Example_UID',
                                                                     completed_by_name='Test User')

            self.assertTrue(updated_order_uid, u'Order not completed')
