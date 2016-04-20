import base64
import error
import json
import unittest
from datetime import datetime

import mock

from error import PexError
from pex import BaseAPI, PEXAPIWrapper, SANDBOX_BASE_URL, JsonEncoder


def generate_mock_api_response(text, status_code=200):
    m = mock.Mock()
    resp = mock.Mock()
    resp.text = text
    resp.status_code = status_code
    m.return_value = resp
    return m


def generate_mock_response(text, status_code=200):
    m = mock.Mock()
    if status_code != 200:
        m.side_effect = PexError(
            message="PexError", request_url="/PexCardRequest",
            request_params={}, status_code=400, response="")
    else:
        m.return_value = json.loads(text)
    return m


class BaseAPITest(unittest.TestCase):
    def setUp(self):
        token = 'TOKEN'
        self.base_api = BaseAPI(token)
        self.methods_to_test = [
            (self.base_api.put, 'requests.put'),
            (self.base_api.post, 'requests.post')
        ]
        self.endpoint = "DummyEndpoint"
        self.data = {'Username': '@fliu'}


class BaseAPIHttpMethodTest(BaseAPITest):
    def test_get_success(self):
        m = generate_mock_api_response(text='{"CardOrderId":2871}')
        with mock.patch('requests.get', m):
            response = self.base_api.get(self.endpoint, data=self.data)
            self.assertEqual(response, {'CardOrderId': 2871})
            m.assert_called_once_with(
                SANDBOX_BASE_URL.format(endpoint=self.endpoint),
                headers={
                    'authorization': 'token {}'.format(self.base_api.token),
                    'content-type': 'application/json'},
                data=self.data
            )

    def test_get_status_raise_exception(self):
        m1 = generate_mock_api_response(text='{"CardOrderId":2871}',
                                        status_code=400)
        with mock.patch('requests.get', m1):
            with self.assertRaises(PexError):
                self.base_api.get(self.endpoint, data=self.data)
            m1.assert_called_once_with(
                SANDBOX_BASE_URL.format(endpoint=self.endpoint),
                headers={
                    'authorization': 'token {}'.format(self.base_api.token),
                    'content-type': 'application/json'},
                data=self.data
            )

    def test_get_error(self):
        m1 = generate_mock_api_response(
            text='{"CardOrderId":2871,"Message":"Card limits exceeded."}',
            status_code=400)
        with mock.patch('requests.get', m1):
            with self.assertRaises(PexError):
                self.base_api.get(self.endpoint, data=self.data)
                m1.assert_called_once_with(
                    SANDBOX_BASE_URL.format(endpoint=self.endpoint),
                    headers={
                        'authorization':
                            'token {}'.format(self.base_api.token),
                        'content-type': 'application/json'},
                    data=self.data
                )

    def test_put_post_success(self):
        for method, method_to_mock in self.methods_to_test:
            m = generate_mock_api_response(text='{"CardOrderId":2871}')
            with mock.patch(method_to_mock, m):
                response = method(self.endpoint, data=self.data)
                self.assertEqual(response, {'CardOrderId': 2871})
                m.assert_called_once_with(
                    SANDBOX_BASE_URL.format(endpoint=self.endpoint),
                    headers={
                        'authorization':
                            'token {}'.format(self.base_api.token),
                        'content-type': 'application/json'},
                    data=json.dumps(self.data, cls=JsonEncoder)
                )

    def test_put_post_status_raise_exception(self):
        for method, method_to_mock in self.methods_to_test:
            m1 = generate_mock_api_response(text='{"CardOrderId":2871}',
                                            status_code=400)
            with mock.patch(method_to_mock, m1):
                with self.assertRaises(PexError):
                    method(self.endpoint, data=self.data)
                m1.assert_called_once_with(
                    SANDBOX_BASE_URL.format(endpoint=self.endpoint),
                    headers={
                        'authorization':
                            'token {}'.format(self.base_api.token),
                        'content-type': 'application/json'},
                    data=json.dumps(self.data, cls=JsonEncoder)
                )

    def test_put_post_error(self):
        for method, method_to_mock in self.methods_to_test:
            m1 = generate_mock_api_response(
                text='{"CardOrderId":2871,"Message":"Card limits exceeded."}',
                status_code=400)
            with mock.patch(method_to_mock, m1):
                with self.assertRaises(PexError):
                    method(self.endpoint, data=self.data)
                m1.assert_called_once_with(
                    SANDBOX_BASE_URL.format(endpoint=self.endpoint),
                    headers={
                        'authorization':
                            'token {}'.format(self.base_api.token),
                        'content-type': 'application/json'},
                    data=json.dumps(self.data, cls=JsonEncoder)
                )


class BaseAPIGetTokenTest(BaseAPITest):
    def test_success(self):
        m = generate_mock_response(text='{"NewToken":"NEW TOKEN"}')
        with mock.patch('pex.BaseAPI.post', m):
            resp = self.base_api.create_token(
                client_id="@fliu",
                client_secret="SECRET",
                username="Frank Liu",
                password="PASSWORD"
            )
            self.assertEqual(resp, json.loads('{"NewToken":"NEW TOKEN"}'))
            authorization = base64.b64encode("@fliu" + ':' + "SECRET")
            m.assert_called_once_with(
                'Token',
                headers={'authorization': 'basic {}'.format(authorization)},
                data={'Username': "Frank Liu", 'Password': "PASSWORD"}
            )

    def test_bad_request(self):
        m = generate_mock_response(text='{"NewToken":"NEW TOKEN"}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.post', m):
            with self.assertRaises(PexError):
                self.base_api.create_token(
                    client_id="@fliu",
                    client_secret="SECRET",
                    username="Frank Liu",
                    password="PASSWORD"
                )
            authorization = base64.b64encode("@fliu" + ':' + "SECRET")
            m.assert_called_once_with(
                'Token',
                headers={'authorization': 'basic {}'.format(authorization)},
                data={'Username': "Frank Liu", 'Password': "PASSWORD"}
            )


class BaseAPIHandleAPIErrorRetrieveJsonTest(BaseAPITest):
    def setUp(self):
        super(BaseAPIHandleAPIErrorRetrieveJsonTest, self).setUp()
        self.test_error_status_code_set = [
            (error.RateLimitError, 429),
            (error.InvalidRequestError, 400),
            (error.InvalidRequestError, 404),
            (error.AuthenticationError, 401),
            (error.RequesterForbiddenError, 403),
            (error.PexServerSideError, 500),
            (error.PexServerSideError, 599),
            (error.APIError, 600)
        ]

    def test_success(self):
        m = generate_mock_api_response(
            text='{"CardOrderId":2871}', status_code=200)
        with mock.patch('requests.get', m):
            response = self.base_api.get(self.endpoint, data=self.data)
            self.assertEqual(response, {'CardOrderId': 2871})

    def test_error_status_codes(self):
        for (error_type, status_code) in self.test_error_status_code_set:
            m = generate_mock_api_response(
                text='{"CardOrderId":2871, "Message":"Wrong"}',
                status_code=status_code)
            with mock.patch('requests.get', m):
                with self.assertRaises(error_type) as cm:
                    self.base_api.get(self.endpoint, data=self.data)
                self.assertEqual(cm.exception.message, "Wrong")

    def test_invalid_json_response(self):
        m = generate_mock_api_response(
            text='{"CardOrderId":2871')
        with mock.patch('requests.get', m):
            with self.assertRaises(error.InvalidPexServerResponseError) as cm:
                self.base_api.get(self.endpoint, data=self.data)
            self.assertEqual(
                cm.exception.message,
                'Invalid Pex json response: {"CardOrderId":2871')


class CardTest(unittest.TestCase):
    def setUp(self):
        token = 'TOKEN'
        self.card = PEXAPIWrapper(token)
        self.valid_data = {"Cards": [{"DateOfBirth": "07-18-1988",
                             "Email": "test@pm.com",
                             "FirstName": "Salar",
                             "LastName": unicode("Khan", "utf-8"),
                             "Phone": "1234567890",
                             "ProfileAddress": {
                                 "State": unicode("CA", "utf-8")},
                             "ShippingAddress": {},
                             "ShippingMethod": "FirstClassMail",
                             "ShippingPhone": "1234567890"}]}
        self.invalid_data = {"Cards": [{"DateOfBirth": "07-18-1988",
                             "FirstName": "Salar",
                             "LastName": unicode("Khan", "utf-8"),
                             "Phone": "1234567890",
                             "ProfileAddress": {
                                 "State": unicode("CA", "utf-8")},
                             "ShippingAddress": {},
                             "ShippingMethod": "FirstClassMail",
                             "ShippingPhone": "1234567890"}]}


class CardValidateTest(CardTest):
    def test_success(self):
        r_data = PEXAPIWrapper.validate(self.valid_data)
        self.assertEqual(self.valid_data, r_data)

    def test_fail(self):
        with self.assertRaises(ValueError):
            PEXAPIWrapper.validate(self.invalid_data)


class CardCreateTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"CardOrderId":2871}')
        with mock.patch('pex.BaseAPI.post', m):
            resp = self.card.create(self.valid_data)
            m.assert_called_once_with(
                "Card/CreateAsync",
                data=self.valid_data
            )
            self.assertEqual(resp, json.loads('{"CardOrderId":2871}'))

    def test_invalid_card(self):
        m = generate_mock_response(text='{"CardOrderId":2871}')
        with mock.patch('pex.BaseAPI.post', m):
            with self.assertRaises(ValueError):
                self.card.create(self.invalid_data)

    def test_bad_request(self):
        m = generate_mock_response(text='{"CardOrderId":2871}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.post', m):
            with self.assertRaises(PexError):
                self.card.create(self.valid_data)
            m.assert_called_once_with(
                "Card/CreateAsync",
                data=self.valid_data
            )


class CardActivateTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"Activated":2871}')
        with mock.patch('pex.BaseAPI.post', m):
            resp = self.card.activate(card_id=1234)
            m.assert_called_once_with(
                "Card/Activate/1234"
            )
            self.assertEqual(resp, json.loads('{"Activated":2871}'))

    def test_no_card_id(self):
        with self.assertRaises(ValueError):
            self.card.activate()

    def test_bad_request(self):
        m = generate_mock_response(text='{"Activated":2871}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.post', m):
            with self.assertRaises(PexError):
                self.card.activate(card_id=1234)
            m.assert_called_once_with(
                "Card/Activate/1234"
            )


class CardFundTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"Funded":1234}')
        with mock.patch('pex.BaseAPI.post', m):
            resp = self.card.fund(card_id=1234, amount=200)
            m.assert_called_once_with(
                "Card/Fund/1234",
                data={"Amount": 200}
            )
            self.assertEqual(resp, json.loads('{"Funded":1234}'))

    def test_no_card_id(self):
        with self.assertRaises(ValueError):
            self.card.fund(amount=200)

    def test_no_amount(self):
        with self.assertRaises(ValueError):
            self.card.fund(card_id=1234)

    def test_bad_request(self):
        m = generate_mock_response(text='{"Funded":1234}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.post', m):
            with self.assertRaises(PexError):
                self.card.fund(card_id=1234, amount=200)
            m.assert_called_once_with(
                "Card/Fund/1234",
                data={"Amount": 200}
            )


class CardBlockTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"Blocked":1234}')
        with mock.patch('pex.BaseAPI.put', m):
            resp = self.card.block(card_id=1234)
            self.assertEqual(resp, json.loads('{"Blocked":1234}'))
            m.assert_called_once_with(
                "Card/Status/1234",
                data={"Status": "Blocked"}
            )

    def test_no_card_id(self):
        with self.assertRaises(ValueError):
            self.card.block()

    def test_bad_request(self):
        m = generate_mock_response(text='{"Blocked":1234}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.put', m):
            with self.assertRaises(PexError):
                self.card.block(card_id=1234)
            m.assert_called_once_with(
                "Card/Status/1234",
                data={"Status": "Blocked"}
            )


class CardUnblockTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"Unblocked":1234}')
        with mock.patch('pex.BaseAPI.put', m):
            resp = self.card.unblock(card_id=1234)
            self.assertEqual(resp, json.loads('{"Unblocked":1234}'))
            m.assert_called_once_with(
                "Card/Status/1234",
                data={"Status": "Active"}
            )

    def test_no_card(self):
        with self.assertRaises(ValueError):
            self.card.unblock()

    def test_bad_request(self):
        m = generate_mock_response(text='{"Unblocked":1234}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.put', m):
            with self.assertRaises(PexError):
                self.card.unblock(card_id=1234)
            m.assert_called_once_with(
                "Card/Status/1234",
                data={"Status": "Active"}
            )


class CardZeroBalanceTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"Zeroed":1234}')
        with mock.patch('pex.BaseAPI.post', m):
            resp = self.card.zero_balance(card_id=1234)
            self.assertEqual(resp, json.loads('{"Zeroed":1234}'))
            m.assert_called_once_with(
                "Card/Zero/1234"
            )

    def test_no_card_id(self):
        with self.assertRaises(ValueError):
            self.card.zero_balance()

    def test_bad_requst(self):
        m = generate_mock_response(text='{"Zeroed":1234}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.post', m):
            with self.assertRaises(PexError):
                self.card.zero_balance(card_id=1234)
            m.assert_called_once_with(
                "Card/Zero/1234",
            )


class CardGetOrderTest(CardTest):
    def test_success(self):
        m = generate_mock_response(text='{"Order":1234}')
        with mock.patch('pex.BaseAPI.get', m):
            resp = self.card.get_order(card_order_id=1234)
            self.assertEqual(resp, json.loads('{"Order":1234}'))
            m.assert_called_once_with(
                "Card/CardOrder/1234"
            )

    def test_no_card_order_id(self):
        with self.assertRaises(ValueError):
            self.card.get_order(card_order_id=None)

    def test_bad_request(self):
        m = generate_mock_response(text='{"Order":1234}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.get', m):
            with self.assertRaises(PexError):
                self.card.get_order(card_order_id=1234)
            m.assert_called_once_with(
                "Card/CardOrder/1234"
            )


class DetailsTest(unittest.TestCase):
    def setUp(self):
        token = "TOKEN"
        self.details = PEXAPIWrapper(token)
        self.start_dt = datetime(2015, 7, 14, 12, 30)
        self.end_dt = datetime(2015, 7, 17, 12, 30)


class DetailsGetTransactionListTest(DetailsTest):
    def test_success(self):
        m = generate_mock_response(text='{"TransactionList":"DummyList"}')
        with mock.patch('pex.BaseAPI.get', m):
            resp = self.details.get_transaction_list(
                start_date=self.start_dt,
                end_date=self.end_dt,
                include_declines=True,
                include_pendings=True
            )
            self.assertEqual(resp,
                             json.loads('{"TransactionList":"DummyList"}'))
            m.assert_called_once_with(
                'Details/AllCardholderTransactions?'
                'StartDate=2015-07-14T12%3A30%3A00&'
                'IncludeDeclines=True&'
                'IncludePendings=True&'
                'EndDate=2015-07-17T12%3A30%3A00'
            )

    def test_no_start_date(self):
        with self.assertRaises(ValueError):
            self.details.get_transaction_list(
                start_date=None,
                end_date=self.end_dt)

    def test_no_end_date(self):
        with self.assertRaises(ValueError):
            self.details.get_transaction_list(
                start_date=self.start_dt,
                end_date=None)

    def test_bad_request(self):
        m = generate_mock_response(
            text='{"TransactionList":"DummyList"}', status_code=400)
        with mock.patch('pex.BaseAPI.get', m):
            with self.assertRaises(PexError):
                self.details.get_transaction_list(
                    start_date=self.start_dt,
                    end_date=self.end_dt,
                    include_declines=True,
                    include_pendings=True
                )
            m.assert_called_once_with(
                'Details/AllCardholderTransactions?'
                'StartDate=2015-07-14T12%3A30%3A00&'
                'IncludeDeclines=True&'
                'IncludePendings=True&'
                'EndDate=2015-07-17T12%3A30%3A00'
            )


class DetailsGetAccountTest(DetailsTest):
    def test_success(self):
        m = generate_mock_response(text='{"AccountDetail":"DummyDetail"}')
        with mock.patch('pex.BaseAPI.get', m):
            resp = self.details.get_account(account_id=1234)
            self.assertEqual(resp,
                             json.loads('{"AccountDetail":"DummyDetail"}'))
            m.assert_called_once_with(
                "Details/AccountDetails/1234"
            )

    def test_no_account_id(self):
        with self.assertRaises(ValueError):
            self.details.get_account()

    def test_bad_request(self):
        m = generate_mock_response(text='{"AccountDetail":"DummyDetail"}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.get', m):
            with self.assertRaises(PexError):
                self.details.get_account(account_id=1234)
            m.assert_called_once_with(
                "Details/AccountDetails/1234"
            )


class DetailsGetAllAccountsTest(DetailsTest):
    def test_success(self):
        m = generate_mock_response(text='{"AccountDetail":"DummyDetail"}')
        with mock.patch('pex.BaseAPI.get', m):
            resp = self.details.get_all_accounts()
            self.assertEqual(resp,
                             json.loads('{"AccountDetail":"DummyDetail"}'))
            m.assert_called_once_with(
                "Details/AccountDetails"
            )

    def test_bad_request(self):
        m = generate_mock_response(text='{"AccountDetail":"DummyDetail"}',
                                   status_code=400)
        with mock.patch('pex.BaseAPI.get', m):
            with self.assertRaises(PexError):
                self.details.get_all_accounts()
            m.assert_called_once_with(
                "Details/AccountDetails"
            )


if __name__ == '__main__':
    unittest.main()
