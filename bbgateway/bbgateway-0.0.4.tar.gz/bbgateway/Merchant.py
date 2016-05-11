from urllib.parse import urlencode, parse_qsl

import requests


class Merchant:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def to_dict(self):
        return {'username': self.username, 'password': self.password}

    def format_login_information(self):
        return urlencode({'username': self.username, 'password': self.password})

    def sale(self, order, shipping, billing, credit_card):
        """
        Performs a Sale with Bankcard Brokers Gateway
        :param order: Order object
        :param shipping: Shipping object
        :param billing: Billing object
        :param credit_card: CreditCard object
        :return:
        """
        data = self.to_dict()
        data.update(order.to_dict())
        data.update(shipping.to_dict())
        data.update(billing.to_dict())
        data.update(credit_card.to_dict())
        data['type'] = "sale"

        response = self.send_post_request(data)
        # status_code = response.status_code
        # parse response into a dict
        return dict(parse_qsl(response.text))

    def authorization(self, order, shipping, billing, credit_card):
        """
        Performs a authorization of the order using the shipping, billing and credit card information provided
        :param order: the order to be authorized
        :param shipping: the shipping information
        :param billing: the billing information
        :param credit_card: the credit card information
        :return:
        """
        data = self.to_dict()
        data.update(order.to_dict())
        data.update(shipping.to_dict())
        data.update(billing.to_dict())
        data.update(credit_card.to_dict())
        data['type'] = "auth"

        response = self.send_post_request(data)
        # status_code = response.status_code
        # parse response into a dict
        return dict(parse_qsl(response.text))

    def capture(self, transaction_id, amount):
        """
        Performs the capture of a previous authorized transaction
        :param transaction_id: the pre-authorized transaction identifier
        :param amount: an amount less or equals than the authorized one
        :return:
        """
        data = self.to_dict()
        data['type'] = "capture"
        data['transactionid'] = transaction_id
        data['amount'] = amount

        response = self.send_post_request(data)
        # status_code = response.status_code
        # parse response into a dict
        return dict(parse_qsl(response.text))

    def send_post_request(self, data):
        url = 'https://secure.bankcardbrokersgateway.com/api/transact.php'
        return requests.post(url, data=data)
