# -*- coding: utf-8 -*-
"""
    koalaecommerce.paymentgateways.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Koala ecommerce payment gateways. Ideally this will move to an external location so that people can add third party
    payment providers. As part of the Alpha it is enclosed in the module.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""
from Crypto.Cipher import AES
from Crypto import Random
import unicodedata
import urlparse
from decimal import Decimal
import datetime
from xml.etree import ElementTree
from koalaecommerce.basepaymentgateway import BasePaymentGateway, BasePaymentGatewayRequest, BaseOrderSanitizer, \
    PaymentGatewayResponse


BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


class AESCipher:
    def __init__(self, key):
        """
        Requires hex encoded param as a key
        """
        self.key = key.decode("hex")

    def encrypt(self, raw, iv=None):
        """
        Returns hex encoded encrypted value!
        :param iv:
        :param raw:
        """
        # raw.decode('ascii')
        # raw.encode('utf-8')
        raw = unicodedata.normalize('NFKD', raw).encode('ascii', 'ignore')
        if not iv:
            iv = Random.new().read(AES.block_size)

        raw = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(raw).encode("hex").upper()

    def decrypt(self, enc, iv=None):
        """
        Requires hex encoded param to decrypt
        :param enc:
        :param iv:
        """
        enc = enc.decode("hex")
        if not iv:
            iv = enc[:16]
        # enc = enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc))


def encrypt_payload(payload, vendor_key, iv):
    aes = AESCipher(vendor_key.encode("hex"))
    return '@' + aes.encrypt(raw=payload, iv=iv)


def decrypt_payload(payload, vendor_key):
    payload = payload.replace("@", "", 1)
    aes = AESCipher(vendor_key.encode("hex"))
    return aes.decrypt(enc=payload, iv=vendor_key)


class SagePayRequest(BasePaymentGatewayRequest):
    title = 'SagePay'

    def __init__(self, encrypted_payload, txtype='PAYMENT', vpsprotocol=3.00, **kwargs):
        if not encrypted_payload:
            raise ValueError
        self.vpsprotocol = vpsprotocol
        self.crypt = encrypted_payload
        self.txtype = txtype
        super(SagePayRequest, self).__init__(**kwargs)


class SagePayOrderSanitizer(BaseOrderSanitizer):
    @classmethod
    def sanitize_order(cls, order):
        # The SagePay request will fail without these values set. It's a hack but it prevents users from seeing errors
        if order.billing_country == 'US' and not order.billing_state:
            order.billing_state = 'WA'
        elif order.billing_country != 'US' and not order.billing_post_code:
            order.billing_post_code = '000'
        if order.delivery_country == 'US' and not order.delivery_state:
            order.delivery_state = 'WA'
        elif order.delivery_country != 'US' and not order.delivery_post_code:
            order.delivery_post_code = '000'
        return super(SagePayOrderSanitizer, cls).sanitize_order(order=order)


class SagePay(BasePaymentGateway):
    _sanitizer = SagePayOrderSanitizer

    @classmethod
    def _encode_request(cls, sanitized_order, gateway_config, **kwargs):
        try:
            gateway_config['success_url'] = gateway_config['success_url'].format(request_signature=kwargs['request_signature'])
        except (NameError, KeyError):
            # Either the success_url doesn't contain the request_signature anchor or request_signature is not supplied
            pass

        try:
            gateway_config['failure_url'] = gateway_config['failure_url'].format(request_signature=kwargs['request_signature'])
        except (NameError, KeyError):
            # Either the success_url doesn't contain the request_signature anchor or request_signature is not supplied
            pass

        gateway_config['merchant_info'] = cls._sanitizer.sanitize_merchant(gateway_config['merchant_info'])
        gateway_config['success_url'] = cls._sanitizer.sanitize_url(gateway_config['success_url'])
        gateway_config['failure_url'] = cls._sanitizer.sanitize_url(gateway_config['failure_url'])

        # Build payment success email message
        merchant_name = gateway_config['merchant_info']['name']
        merchant_vat_num = gateway_config['merchant_info']['vat_number']
        merchant_registered_address = gateway_config['merchant_info']['registered_address']
        merchant_success_message = gateway_config['merchant_info']['success_message']
        registered_addr_str = ''
        vat_num_str = ''

        if sanitized_order.customer_company_name:
            customer_str = unicode(sanitized_order.customer_company_name)
        else:
            customer_str = unicode('{} {}'.format(sanitized_order.customer_first_name,
                                                  sanitized_order.customer_last_name))
        if merchant_vat_num:
            vat_num_str = '{0}'.format(merchant_vat_num)
        if merchant_registered_address:
            registered_addr_str = '{0}'.format(merchant_registered_address)

        sanitized_success_message = cls._sanitizer.sanitize_confirmation_message(merchant_success_message.format(customer=customer_str,
                                                                                                                 merchant_name=merchant_name,
                                                                                                                 merchant_vat_number=vat_num_str,
                                                                                                                 merchant_registered_address=registered_addr_str))

        # Build basket string for payload
        if gateway_config['basket_type'] == 'simple':
            sanitized_basket = cls.generate_simple_basket(basket=sanitized_order.basket)
            basket = u'&Basket={basket}'
        else:
            sanitized_basket = cls.generate_xml_basket(basket=sanitized_order.basket)
            basket = u'&BasketXML={basket}'

        main = u'VendorTxCode={transaction_reference}&Amount={order_total}&Currency={currency}&Description={order_description}&CustomerName={customer_name}&CustomerEMail={contact_email}&BillingSurname={billing_surname}&BillingFirstnames={billing_first_names}&BillingAddress1={billing_address_1}&BillingAddress2={billing_address_2}&BillingCity={billing_city}&BillingPostCode={billing_post_code}&BillingCountry={billing_country}&BillingPhone={billing_phone}&DeliverySurname={delivery_surname}&DeliveryFirstnames={delivery_first_names}&DeliveryAddress1={delivery_address_1}&DeliveryAddress2={delivery_address_2}&DeliveryCity={delivery_city}&DeliveryPostCode={delivery_post_code}&DeliveryCountry={delivery_country}&DeliveryPhone={delivery_phone}&SuccessURL={success_url}&FailureURL={failure_url}&VendorEMail={vendor_emails}&SendEMail={send_confirmation_message}&eMailMessage={confirmation_message}&Website={merchant_website}'

        main += basket

        if sanitized_order.billing_country == 'US':
            main += u'&BillingState={}&DeliveryState={}'.format(sanitized_order.billing_state,
                                                                sanitized_order.delivery_state)

        payload = main.format(transaction_reference=sanitized_order.order_reference,
                              order_total=sanitized_order.total,
                              currency=sanitized_order.currency,
                              order_description=gateway_config['merchant_info']['description'],
                              customer_name=customer_str,
                              contact_email=sanitized_order.customer.email,
                              billing_surname=sanitized_order.customer_last_name,
                              billing_first_names=sanitized_order.customer_first_name,
                              billing_address_1=sanitized_order.billing_address_1,
                              billing_address_2=sanitized_order.billing_address_2,
                              billing_city=sanitized_order.billing_city,
                              billing_post_code=sanitized_order.billing_post_code,
                              billing_country=sanitized_order.billing_country,
                              billing_phone=sanitized_order.customer_phone,
                              delivery_surname=sanitized_order.customer_last_name,
                              delivery_first_names=sanitized_order.customer_first_name,
                              delivery_address_1=sanitized_order.delivery_address_1,
                              delivery_address_2=sanitized_order.delivery_address_2,
                              delivery_city=sanitized_order.delivery_city,
                              delivery_post_code=sanitized_order.delivery_post_code,
                              delivery_country=sanitized_order.delivery_country,
                              delivery_phone=sanitized_order.customer_phone,
                              success_url=gateway_config['success_url'],
                              failure_url=gateway_config['failure_url'],
                              vendor_emails=gateway_config['merchant_info']['notification_emails'],
                              send_confirmation_message=gateway_config['merchant_info']['send_confirmation'],
                              confirmation_message=sanitized_success_message,
                              merchant_website=gateway_config['merchant_info']['website'],
                              basket=sanitized_basket)

        encrypted_payload = encrypt_payload(payload=payload,
                                            vendor_key=gateway_config['encryption_key'],
                                            iv=gateway_config['encryption_iv'])

        additional_kwargs = {}

        if gateway_config['payment_gateway'] == 'sagepay_test':
            additional_kwargs['title'] = 'SagePay Test Server'

        return SagePayRequest(vendor=gateway_config['vendor'],
                              endpoint=gateway_config['endpoint_url'],
                              encrypted_payload=encrypted_payload, **additional_kwargs)

    @classmethod
    def _decode_response(cls, gateway_response, gateway_config, **kwargs):
        decrypted_payload = decrypt_payload(payload=gateway_response, vendor_key=gateway_config['encryption_key'])
        parsed_response = dict(urlparse.parse_qsl(decrypted_payload))

        success = True if parsed_response['Status'] == 'OK' else False
        method = 'SagePay Test' if gateway_config['payment_gateway'] == 'sagepay_test' else 'SagePay'

        return PaymentGatewayResponse(gateway_transaction_uid=parsed_response['VPSTxId'],
                                      order_reference=parsed_response['VendorTxCode'],
                                      amount=parsed_response['Amount'].replace(',', ''),
                                      timestamp=datetime.datetime.now(),
                                      method=method,
                                      encoded_response=gateway_response,
                                      success=success,
                                      status=parsed_response['Status'],
                                      additional_details={
                                          'gateway_message': parsed_response['StatusDetail'],
                                          'card_type': parsed_response.get('CardType', ''),
                                      })

    @staticmethod
    def _filter_decoded_response(decrypted_response):
        return

    @staticmethod
    def generate_simple_basket(basket):
        items = []

        for cartline in basket:
            sage_product_code = getattr(cartline.product, 'sage_sku', '')
            if sage_product_code:
                sage_product_code = '[0]'.format(sage_product_code)

            product_name = getattr(cartline.product, 'title', None)
            if not product_name:
                product_name = getattr(cartline.product, 'sku', 'Order Item')

            item_parts = ['{0}{1}'.format(sage_product_code, product_name),
                          str(cartline.get_quantity()),
                          str(Decimal(cartline.get_total()[0]).quantize(Decimal(10) ** -2)),
                          str(Decimal(cartline.get_total()[1] - cartline.get_total()[0]).quantize(Decimal(10) ** -2)),
                          str(Decimal(cartline.get_total()[1]).quantize(Decimal(10) ** -2)),
                          str(Decimal(cartline.get_total()[1]).quantize(Decimal(10) ** -2))]

            items.append(':'.join(item_parts))

        simple_basket = str(len(items)) + ':' + (':'.join(items))
        return simple_basket

    @staticmethod
    def generate_xml_basket(basket):
        xml_basket = ElementTree.Element("basket")
        for cartline in basket:
            item = ElementTree.SubElement(basket, "item")

            product_name = getattr(cartline.product, 'title', None)
            if not product_name:
                product_name = getattr(cartline.product, 'sku', 'Order Item')

            description = ElementTree.SubElement(item, "description")
            description.text = product_name

            productSku = ElementTree.SubElement(item, "productSku")
            productSku.text = getattr(cartline.product, 'sage_sku', '')

            productCode = ElementTree.SubElement(item, "productCode")
            productCode.text = getattr(cartline.product, 'sage_sku', '')

            quantity = ElementTree.SubElement(item, "quantity")
            quantity.text = cartline.get_quantity()

            unitNetAmount = ElementTree.SubElement(item, "unitNetAmount")
            # unitNetAmount.text = cartline.get_total().net()
            unitNetAmount.text = str(Decimal(cartline.get_total()[0]).quantize(Decimal(10) ** -2))
            unitTaxAmount = ElementTree.SubElement(item, "unitTaxAmount")
            # unitTaxAmount.text = cartline.get_total().gross() - cartline.get_total().net()
            unitTaxAmount.text = str(Decimal(cartline.get_total()[1] - cartline.get_total()[0]).quantize(Decimal(10) ** -2))
            unitGrossAmount = ElementTree.SubElement(item, "unitGrossAmount")
            # unitGrossAmount.text = cartline.get_total().gross()
            unitGrossAmount.text = str(Decimal(cartline.get_total()[1]).quantize(Decimal(10) ** -2))
            totalGrossAmount = ElementTree.SubElement(item, "totalGrossAmount")
            # totalGrossAmount.text = cartline.get_total().gross()
            totalGrossAmount.text = str(Decimal(cartline.get_total()[1]).quantize(Decimal(10) ** -2))

        return ElementTree.tostring(xml_basket)


def _offline_payment_request_encoder(sanitized_order, gateway_config):
    main = u'OrderRef={order_ref}&Amount={amount}&Currency={currency}&SuccessURL={success_url}&FailureURL={failure_url}'
    return main.format(order_ref=sanitized_order.order_reference,
                       amount=sanitized_order.total,
                       currency=sanitized_order.currency,
                       success_url=gateway_config['success_url'],
                       failure_url=gateway_config['failure_url'])


def _offline_payment_response_decoder(decrypted_response, gateway_config):
    return dict(urlparse.parse_qsl(decrypted_response))


class BACSRequest(BasePaymentGatewayRequest):
    title = 'BACS'

    def __init__(self, encrypted_payload, **kwargs):
        self.encrypted_payload = encrypted_payload
        super(BACSRequest, self).__init__(**kwargs)


class BACS(BasePaymentGateway):
    @classmethod
    def _encode_request(cls, sanitized_order, gateway_config, **kwargs):
        try:
            gateway_config['success_url'] = gateway_config['success_url'].format(request_signature=kwargs['request_signature'])
        except (NameError, KeyError):
            # Either the success_url doesn't contain the request_signature anchor or request_signature is not supplied
            pass

        try:
            gateway_config['failure_url'] = gateway_config['failure_url'].format(request_signature=kwargs['request_signature'])
        except (NameError, KeyError):
            # Either the success_url doesn't contain the request_signature anchor or request_signature is not supplied
            pass

        gateway_config['success_url'] = cls._sanitizer.sanitize_url(gateway_config['success_url'])
        gateway_config['failure_url'] = cls._sanitizer.sanitize_url(gateway_config['failure_url'])
        payload = _offline_payment_request_encoder(sanitized_order=sanitized_order, gateway_config=gateway_config)

        encrypted_payload = encrypt_payload(payload=payload,
                                            vendor_key=gateway_config['encryption_key'],
                                            iv=gateway_config['encryption_iv'])

        return BACSRequest(vendor=gateway_config['vendor'],
                           endpoint=gateway_config['endpoint_url'],
                           encrypted_payload=encrypted_payload)

    @classmethod
    def _decode_response(cls, gateway_response, gateway_config, **kwargs):
        decrypted_payload = decrypt_payload(payload=gateway_response, vendor_key=gateway_config['encryption_key'])
        parsed_response = _offline_payment_response_decoder(decrypted_response=decrypted_payload,
                                                            gateway_config=gateway_config)

        success = True if parsed_response['Status'] == 'OK' else False

        return PaymentGatewayResponse(gateway_transaction_uid=None,
                                      order_reference=parsed_response['OrderRef'],
                                      amount=parsed_response['Amount'],
                                      timestamp=datetime.datetime.now(),
                                      method='BACS',
                                      encoded_response=gateway_response,
                                      success=success,
                                      status=parsed_response['Status'],
                                      additional_details=None)


class ChequeRequest(BasePaymentGatewayRequest):
    title = 'Cheque'

    def __init__(self, encrypted_payload, **kwargs):
        self.encrypted_payload = encrypted_payload
        super(ChequeRequest, self).__init__(**kwargs)


class Cheque(BasePaymentGateway):
    @classmethod
    def _encode_request(cls, sanitized_order, gateway_config, **kwargs):
        try:
            gateway_config['success_url'] = gateway_config['success_url'].format(request_signature=kwargs['request_signature'])
        except (NameError, KeyError):
            # Either the success_url doesn't contain the request_signature anchor or request_signature is not supplied
            pass

        try:
            gateway_config['failure_url'] = gateway_config['failure_url'].format(request_signature=kwargs['request_signature'])
        except (NameError, KeyError):
            # Either the success_url doesn't contain the request_signature anchor or request_signature is not supplied
            pass

        gateway_config['success_url'] = cls._sanitizer.sanitize_url(gateway_config['success_url'])
        gateway_config['failure_url'] = cls._sanitizer.sanitize_url(gateway_config['failure_url'])
        payload = _offline_payment_request_encoder(sanitized_order=sanitized_order, gateway_config=gateway_config)

        encrypted_payload = encrypt_payload(payload=payload,
                                            vendor_key=gateway_config['encryption_key'],
                                            iv=gateway_config['encryption_iv'])

        return ChequeRequest(vendor=gateway_config['vendor'],
                             endpoint=gateway_config['endpoint_url'],
                             encrypted_payload=encrypted_payload)

    @classmethod
    def _decode_response(cls, gateway_response, gateway_config, **kwargs):
        decrypted_payload = decrypt_payload(payload=gateway_response, vendor_key=gateway_config['encryption_key'])
        parsed_response = _offline_payment_response_decoder(decrypted_response=decrypted_payload,
                                                            gateway_config=gateway_config)

        success = True if parsed_response['Status'] == 'OK' else False

        return PaymentGatewayResponse(gateway_transaction_uid=None,
                                      order_reference=parsed_response['OrderRef'],
                                      amount=parsed_response['Amount'],
                                      timestamp=datetime.datetime.now(),
                                      method='Cheque',
                                      encoded_response=gateway_response,
                                      success=success,
                                      status=parsed_response['Status'],
                                      additional_details=None)
