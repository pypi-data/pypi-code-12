import copy
from decimal import Decimal


class BasePaymentGatewayRequest(object):
    title = 'Base Payment Request'

    def __init__(self, endpoint, vendor=None, title=None):
        self.endpoint = endpoint
        self.vendor = vendor
        if title is not None:
            self.title = title

    @property
    def id(self):
        return self.title.replace(" ", "").lower()


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


class BaseOrderSanitizer(object):
    @classmethod
    def sanitize_order(cls, order):
        order.order_reference = cls.sanitize_order_reference(order.order_reference)
        order.order_type = cls.sanitize_order_type(order.order_type)
        order.order_complete = cls.sanitize_order_complete(order.order_complete)
        order.customer_uid = cls.sanitize_customer_uid(order.customer_uid)
        order.user_uid = cls.sanitize_user_uid(order.user_uid)
        order.customer_first_name = cls.sanitize_customer_first_name(order.customer_first_name)
        order.customer_last_name = cls.sanitize_customer_last_name(order.customer_last_name)
        order.customer_company_name = cls.sanitize_customer_company_name(order.customer_company_name)
        order.customer_email = cls.sanitize_customer_email(order.customer_email)
        order.customer_phone = cls.sanitize_customer_phone(order.customer_phone)
        order.customer_turnover_ltm = cls.sanitize_customer_turnover_ltm(order.customer_turnover_ltm)
        order.customer_tax_number = cls.sanitize_customer_tax_number(order.customer_tax_number)
        order.customer_membership_number = cls.sanitize_customer_membership_number(order.customer_membership_number)
        order.delivery_address_1 = cls.sanitize_address_1(order.delivery_address_1)
        order.delivery_address_2 = cls.sanitize_address_2(order.delivery_address_2)
        order.delivery_city = cls.sanitize_city(order.delivery_city)
        order.delivery_country = cls.sanitize_country(order.delivery_country)
        order.delivery_state = cls.sanitize_state(order.delivery_state)
        order.delivery_post_code = cls.sanitize_post_code(order.delivery_post_code)
        order.billing_address_1 = cls.sanitize_address_1(order.billing_address_1)
        order.billing_address_2 = cls.sanitize_address_2(order.billing_address_2)
        order.billing_city = cls.sanitize_city(order.billing_city)
        order.billing_country = cls.sanitize_country(order.billing_country)
        order.billing_state = cls.sanitize_state(order.billing_state)
        order.billing_post_code = cls.sanitize_post_code(order.billing_post_code)

        basket_total = order.basket.get_total()
        order.total = cls.sanitize_price(basket_total.gross)
        order.currency = cls.sanitize_currency(basket_total.currency)
        return order

    @staticmethod
    def sanitize_order_reference(order_reference):
        try:
            return unicode(order_reference.strip()[:40])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_order_type(order_type):
        try:
            return unicode(order_type.strip()[:40])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_user_uid(user_uid):
        try:
            return unicode(user_uid.strip()[:255])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_order_complete(order_complete):
        try:
            return unicode(order_complete)
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_uid(customer_uid):
        try:
            return unicode(customer_uid.strip()[:255])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_first_name(customer_first_name):
        try:
            return unicode(customer_first_name.strip()[:20])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_last_name(customer_last_name):
        try:
            return unicode(customer_last_name.strip()[:20])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_company_name(customer_company_name):
        try:
            return unicode(customer_company_name.strip()[:50])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_email(customer_email):
        try:
            return unicode(customer_email.strip()[:255])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_phone(customer_phone):
        try:
            return unicode(customer_phone.strip()[:20])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_turnover_ltm(customer_turnover_ltm):
        try:
            return unicode(customer_turnover_ltm)
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_tax_number(customer_tax_number):
        try:
            return unicode(customer_tax_number.strip()[:20])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_customer_membership_number(customer_membership_number):
        try:
            return unicode(customer_membership_number.strip()[:50])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_address_1(delivery_address_1):
        try:
            return unicode(delivery_address_1.strip()[:100])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_address_2(delivery_address_2):
        try:
            return unicode(delivery_address_2.strip()[:100])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_city(delivery_city):
        try:
            return unicode(delivery_city.strip()[:40])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_country(delivery_country):
        try:
            return unicode(delivery_country.strip()[:2])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_state(delivery_state):
        try:
            return unicode(delivery_state.strip()[:2])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_post_code(delivery_post_code):
        try:
            return unicode(delivery_post_code.strip()[:10])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_currency(currency):
        try:
            return unicode(currency.strip()[:3])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_url(url):
        try:
            return unicode(url.strip()[:2000])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_price(price):
        try:
            return unicode(Decimal(price).quantize(Decimal(10) ** -2))
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_description(description):
        try:
            return unicode(description.strip()[:100])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_vendor_email(vendor_email):
        try:
            return unicode(vendor_email.strip()[:255])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_send_confirmation_email(send_confirmation_email):
        try:
            return unicode(1 if send_confirmation_email else 0)
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_confirmation_message(message):
        try:
            return unicode(message.strip()[:7500])
        except AttributeError:
            return u''

    @staticmethod
    def sanitize_website(website):
        try:
            return unicode(website.strip()[:100])
        except AttributeError:
            return u''

    @classmethod
    def sanitize_merchant(cls, merchant_info):
        merchant_info['description'] = cls.sanitize_description('{0} Order'.format(merchant_info['description']))
        merchant_info['website'] = cls.sanitize_website(merchant_info['website'])
        merchant_info['notification_emails'] = cls.sanitize_vendor_email(merchant_info['notification_emails'])
        merchant_info['send_confirmation'] = cls.sanitize_send_confirmation_email(merchant_info['send_confirmation'])
        return merchant_info


class BasePaymentGateway(object):
    name = 'base'
    _sanitizer = BaseOrderSanitizer

    @classmethod
    def generate_request(cls, order, gateway_config, **kwargs):
        """
        Should parse an order object and return a payment gateway request object
        :param gateway_config:
        :param order:
        :return:
        """
        # We don't want to modify the passed order object directly, even if the values need to be cleaned.
        sanitized_order = cls._sanitizer.sanitize_order(order=copy.deepcopy(order))
        return cls._encode_request(sanitized_order=sanitized_order, gateway_config=gateway_config, **kwargs)

    @classmethod
    def _encode_request(cls, sanitized_order, gateway_config, **kwargs):
        # Return a GatewayRequestObject
        raise NotImplementedError

    @classmethod
    def decode_request(cls, gateway_request, gateway_config, **kwargs):
        # Do whatever processing necessary to decode a request. Only used in rare circumstances e.g. unit testing
        return gateway_request

    @classmethod
    def process_response(cls, gateway_response, gateway_config, **kwargs):
        return cls._decode_response(gateway_response=gateway_response, gateway_config=gateway_config, **kwargs)

    @classmethod
    def _decode_response(cls, gateway_response, gateway_config, **kwargs):
        # Basically you need to process the response data from the gateway and return PaymentGatewayResponse
        raise NotImplementedError
