import requests
import json
from .constants import BASE_URL, BASE_URL_TEST
from .exceptions import PinPaymentsException

class PinPayments(object):

    def __init__(self, test = False, api_secret = None):

        self.api_secret = api_secret

        if test:
            self.base_url = BASE_URL_TEST
        else:
            self.base_url = BASE_URL

    def getCustomers(self, customer_token = None, **kwargs):

        url = self.base_url + '/customers'
        if customer_token:
            url = '/'.join([url, customer_token])

        headers = {'Accept': 'application/json'}

        params = {}

        # Apply any custom parameters passed in
        for key, value in kwargs.items():
            params[key] = value

        response = requests.get(url, params = params, headers = headers, auth = (self.api_secret, ''))

        if response.status_code == 200:

            if not response.headers['content-type'].startswith('application/json'):
                return response.content

            return response.json()

        else:
            raise PinPaymentsException(response)

    def getCustomerCharges(self, customer_token, **kwargs):

        url = '/'.join([self.base_url, 'customers', customer_token, 'charges'])

        headers = {'Accept': 'application/json'}

        params = {}

        # Apply any custom parameters passed in
        for key, value in kwargs.items():
            params[key] = value

        response = requests.get(url, params = params, headers = headers, auth = (self.api_secret, ''))

        if response.status_code == 200:

            if not response.headers['content-type'].startswith('application/json'):
                return response.content

            return response.json()

        else:
            raise PinPaymentsException(response)

    def getCustomerCards(self, customer_token, **kwargs):

        url = '/'.join([self.base_url, 'customers', customer_token, 'cards'])

        headers = {'Accept': 'application/json'}

        params = {}

        # Apply any custom parameters passed in
        for key, value in kwargs.items():
            params[key] = value

        response = requests.get(url, params = params, headers = headers, auth = (self.api_secret, ''))

        if response.status_code == 200:

            if not response.headers['content-type'].startswith('application/json'):
                return response.content

            return response.json()

        else:
            raise PinPaymentsException(response)


    def addCustomer(self, email, card_token = None, card_number = None, card_expiry_month = None,
                    card_expiry_year = None, card_cvc = None, card_name = None, card_address_line1 = None,
                    card_address_line2 = None, card_address_city = None, card_address_postcode = None, 
                    card_address_state = None, card_address_country = None):

        url = self.base_url + '/customers'

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        data = {
            'email': email
        }

        if card_token:
            data['card_token'] = card_token
        else:    
            data['card'] = {
                'number': card_number,
                'expiry_month': card_expiry_month,
                'expiry_year': card_expiry_year,
                'cvc': card_cvc,
                'name': card_name,
                'address_line1': card_address_line1,
                'address_line2': card_address_line2,
                'address_city': card_address_city,
                'address_postcode': card_address_postcode,
                'address_state': card_address_state,
                'address_country': card_address_country,
            }

        response = requests.post(url, headers = headers, auth = (self.api_secret, ''), data = json.dumps(data))

        if response.status_code == 201:

            if not response.headers['content-type'].startswith('application/json'):
                return response.content

            return response.json()

        else:
            raise PinPaymentsException(response)

    def updateCustomer(self, customer_token, email = None, card_token = None, card_number = None, card_expiry_month = None,
                    card_expiry_year = None, card_cvc = None, card_name = None, card_address_line1 = None,
                    card_address_line2 = None, card_address_city = None, card_address_postcode = None, 
                    card_address_state = None, card_address_country = None, primary_card_token = None):

        url = '/'.join([self.base_url, 'customers', customer_token])

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        data = {}

        if email:
            data['email'] = email

        if primary_card_token:
            data['primary_card_token'] = primary_card_token
        elif card_token:
            data['card_token'] = card_token
        elif card_number is not None:
            data['card'] = {
                'number': card_number,
                'expiry_month': card_expiry_month,
                'expiry_year': card_expiry_year,
                'cvc': card_cvc,
                'name': card_name,
                'address_line1': card_address_line1,
                'address_line2': card_address_line2,
                'address_city': card_address_city,
                'address_postcode': card_address_postcode,
                'address_state': card_address_state,
                'address_country': card_address_country,
            }

        response = requests.put(url, headers = headers, auth = (self.api_secret, ''), data = json.dumps(data))

        if response.status_code == 200:

            if not response.headers['content-type'].startswith('application/json'):
                return response.content

            return response.json()

        else:
            raise PinPaymentsException(response)

    def deleteCustomer(self, customer_token):

        url = '/'.join([self.base_url, 'customers', customer_token])

        headers = {'Accept': 'application/json'}

        response = requests.delete(url, headers = headers, auth = (self.api_secret, ''))

        if response.status_code == 204:
            return True

        else:
            raise PinPaymentsException(response)
