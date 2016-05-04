import base64
import json
import urllib
from decimal import Decimal

import requests

import error

API_BASE_URL = 'https://coreapi.pexcard.com/v4/{endpoint}'
SANDBOX_BASE_URL = 'https://corebeta.pexcard.com/api/v42/{endpoint}'
CARD_REQUEST_TEMPLATE = {'FirstName', 'LastName', 'Phone', 'ShippingPhone',
                        'ShippingMethod', 'DateOfBirth', 'Email',
                        'ProfileAddress', 'ShippingAddress'}
API_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        else:
            return super(JsonEncoder, self).default(o)


class BaseAPI(object):
    def __init__(self, token=None, sandbox=False, api_base_url=None):
        self.token = token

        if api_base_url:
            self.api_base_url = api_base_url
        else:
            self.api_base_url = SANDBOX_BASE_URL if sandbox else API_BASE_URL


    def _request(self, method, endpoint, **kwargs):
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['authorization'] = 'token {}'.format(self.token)

        headers['content-type'] = 'application/json'

        url = self.api_base_url.format(endpoint=endpoint)
        response = method(url, headers=headers, **kwargs)
        body = self._handle_api_error_retrieve_json(url, kwargs, response)

        return body

    def _handle_api_error_retrieve_json(self, rurl, rargs, response):
        rcode = response.status_code
        try:
            body = json.loads(response.text)
        except ValueError, e:
            raise error.InvalidPexServerResponseError(
                message="Invalid Pex json response: {}".format(response.text),
                request_url=rurl, request_params=rargs,
                status_code=rcode, response=response)
        err = body.get('Message', None)

        if rcode >= 300:
            err_params = {
                "message": err,
                "request_url": rurl,
                "request_params": rargs, "status_code": rcode,
                "response": response
            }
            if rcode == 429:
                raise error.RateLimitError(**err_params)
            elif rcode in [400, 404]:
                raise error.InvalidRequestError(**err_params)
            elif rcode == 401:
                raise error.AuthenticationError(**err_params)
            elif rcode == 403:
                raise error.RequesterForbiddenError(**err_params)
            elif 500 <= rcode < 600:
                raise error.PexServerSideError(**err_params)
            else:
                raise error.APIError(**err_params)
        else:
            return body

    def create_token(self, **kwargs):
        client_id = kwargs.get('client_id', '')
        client_secret = kwargs.get('client_secret', '')
        authorization = base64.b64encode(client_id + ':' + client_secret)

        headers = {'authorization': 'basic {}'.format(authorization)}

        data = {
            'Username': kwargs.get('username', ''),
            'Password': kwargs.get('password', '')}

        return self.post('Token', headers=headers, data=data)

    def get(self, endpoint, **kwargs):
        return self._request(requests.get, endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        data = kwargs.get('data', {})
        kwargs['data'] = json.dumps(
                data, ensure_ascii=False, cls=JsonEncoder).encode('utf-8')
        return self._request(requests.post, endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        data = kwargs.get('data', {})
        kwargs['data'] = json.dumps(
                data, ensure_ascii=False, cls=JsonEncoder).encode('utf-8')
        return self._request(requests.put, endpoint, **kwargs)


class PEXAPIWrapper(BaseAPI):
    @classmethod
    def create_with_credential(cls, **kwargs):
        wrapper = cls(sandbox=kwargs['sandbox'])
        response = wrapper.create_token(**kwargs)
        wrapper.token = response['Token']
        return wrapper

    @staticmethod
    def validate(request_data):
        template = CARD_REQUEST_TEMPLATE
        cards = request_data['Cards']

        for card in cards:
            if not template.issubset(set(card.keys())):
                raise ValueError('Missing key')

        return request_data

    def create(self, cardholder_info):
        request = PEXAPIWrapper.validate(cardholder_info)
        return self.post("Card/CreateAsync", data=request)

    def activate(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")

        return self.post("Card/Activate/{}".format(card_id))

    def fund(self, card_id=None, amount=None):
        if not card_id:
            raise ValueError("You must specify a card id")
        if not amount:
            raise ValueError("You must specify an amount")

        return self.post("Card/Fund/{}".format(card_id),
                         data={"Amount": amount})

    def block(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")

        return self.put("Card/Status/{}".format(card_id),
                        data={"Status": "Blocked"})

    def unblock(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")
        # check if card is inactive, raise error (or unblock)

        return self.put("Card/Status/{}".format(card_id),
                        data={"Status": "Active"})

    def zero_balance(self, card_id=None):
        if not card_id:
            raise ValueError("You must specify a card id")

        return self.post("Card/Zero/{}".format(card_id))

    def get_order(self, card_order_id):
        if not card_order_id:
            raise ValueError("You must specify a card order id")

        return self.get("Card/CardOrder/{}".format(card_order_id))

    def get_transaction_list(self, start_date, end_date,
                             include_pendings=False, include_declines=False):
        if not start_date:
            raise ValueError("You must specify a start date")
        if not end_date:
            raise ValueError("You must specify a end data")

        params = {
            "StartDate": start_date.strftime(API_TIME_FORMAT),
            "EndDate": end_date.strftime(API_TIME_FORMAT),
            "IncludePendings": include_pendings,
            "IncludeDeclines": include_declines
        }
        url = "Details/AllCardholderTransactions?{params}"\
            .format(params=urllib.urlencode(params))

        return self.get(url)

    def get_account(self, account_id=None):
        if not account_id:
            raise ValueError("You must specify an account id")

        return self.get("Details/AccountDetails/{}".format(account_id))

    def get_all_accounts(self):
        return self.get("Details/AccountDetails")
