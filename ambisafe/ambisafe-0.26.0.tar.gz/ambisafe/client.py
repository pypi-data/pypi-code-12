import logging
import json
import re
from pycoin.encoding import is_valid_wif
import requests

from .account import Account
from .auth import AmbisafeAuth
from .containers import Container
from .exc import ClientError, ServerError
from .transactions import BaseTransaction, Wallet4Transaction, RecoveryTransaction, GrantTransaction

logger = logging.getLogger('ambisafe')


class Client(object):
    def __init__(self, ambisafe_server, secret, api_key, api_secret, account_id_prefix='',
                 connect_timeout=None, read_timeout=None):
        if not re.match(r'^(http|https)://', ambisafe_server):
            raise ValueError('ambisafe_server should be http/https URI')
        self.ambisafe_server = ambisafe_server
        self.secret = secret
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_id_prefix = account_id_prefix + ':' if account_id_prefix else ''
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

    def get_prefixed_account_id(self, account_id):
        return '{}{}'.format(self.account_id_prefix, account_id)

    def remove_prefix_from_account_id(self, account_id):
        if self.account_id_prefix:
            return account_id[len(self.account_id_prefix):]
        return account_id

    def create_simple_account(self, account_id, currency='BTC', wif=None):
        """Create account with Simple security schema
        :param account_id: int|str
        :param currency: str
        :return:
        """
        logger.debug('Creating account with Simple security schema: account_id: {}, currency: {}'
                     .format(account_id, currency))

        data = {
            'id': self.get_prefixed_account_id(account_id),
            'currency': currency,
            'security_schema': 'Simple'
        }

        if wif is not None:
            if not is_valid_wif(wif):
                raise ValueError('Wrong WIF')
            data['containers'] = {'USER': {'wifPk': wif}}

        response = self.make_request('POST', '/accounts', json.dumps(data))

        return Account.from_server_response(response)

    def create_wallet4_account(self, account_id, user_container, operator_container, currency='BTC', version=1):
        """Create account with Wallet4 security schema
        :param account_id: int|str
        :param user_container: ambisafe.account.Container
        :param operator_container: ambisafe.account.Container
        :param currency: str
        :return:
        """
        if version == 1:
            security_schema = 'Wallet4'
        elif version == 2:
            security_schema = 'Wallet4v2'
        else:
            raise ValueError('Wrong Wallet4 version')

        logger.debug(
            'Creating account with {} security schema: account_id: {}, currency: {} '
            'containers: (user: {}, operator: {})'
            .format(
                security_schema,
                self.get_prefixed_account_id(account_id),
                currency,
                user_container,
                operator_container
            )
        )

        containers = {
            "USER": user_container.as_request(),
            "OPERATOR": operator_container.as_request(),
        }
        response = self.make_request('POST', '/accounts', json.dumps({
            'id': self.get_prefixed_account_id(account_id),
            'currency': currency,
            'security_schema': security_schema,
            'containers': containers,
        }))

        return Account.from_server_response(response)

    def create_user_side_key_account(self, account_id, user_container, currency='BTC'):
        """Create account with UserSideKey security schema
        :param account_id: int|str
        :param currency: str
        :return:
        """
        logger.debug('Creating account with UserSideKey security schema: account_id: {}, currency: {}'
                     .format(account_id, currency))

        containers = {
            "USER": user_container.as_request(),
        }

        data = {'id': self.get_prefixed_account_id(account_id),
                'currency': currency,
                'security_schema': 'UserSideKey',
                'containers': containers,
                }

        response = self.make_request('POST', '/accounts', json.dumps(data))

        return Account.from_server_response(response)

    def create_master_wallet_account(self, account_id, signatures_required, containers, currency):
        logger.debug('Creating account with MasterWallet security schema: account_id: {}, currency: {} '
                     'containers: {} signatures_required: {}'
                     .format(self.get_prefixed_account_id(account_id), currency, containers, signatures_required))
        if any(not isinstance(container, Container) for container in containers):
            raise ValueError("containers should be a list of Container instances")

        containers = [dict(role=str(i), **container.as_request()) for i, container in enumerate(containers)]
        response = self.make_request('POST', '/accounts', json.dumps({
            'id': self.get_prefixed_account_id(account_id),
            'currency': currency,
            'security_schema': 'MasterWallet',
            'signatures_required': signatures_required,
            'containers': containers,
        }))
        return Account.from_server_response(response)

    def update_user_side_key_account(self, account_id, user_container, currency='BTC'):

        containers = {
            "USER": user_container.as_request()
        }
        return Account.from_server_response(self.make_request('PUT', '/accounts', json.dumps({
            'id': self.get_prefixed_account_id(account_id),
            'currency': currency,
            'security_schema': 'UserSideKey',
            'containers': containers,
        })))

    def update_wallet4_account(self, account_id, user_container, operator_container,
                               currency='BTC', regenerate_server_container=False, version=1):
        if version == 1:
            security_schema = 'Wallet4'
        elif version == 2:
            security_schema = 'Wallet4v2'
        else:
            raise ValueError('Wrong Wallet4 version')
        containers = {
            "USER": user_container.as_request(),
            "OPERATOR": operator_container.as_request(),
        }
        return Account.from_server_response(self.make_request('PUT', '/accounts', json.dumps({
            'id': self.get_prefixed_account_id(account_id),
            'currency': currency,
            'security_schema': security_schema,
            'containers': containers,
            'regenerate_server_container': regenerate_server_container,
        })))

    def get_balance(self, account_id, currency='BTC'):
        balance = self.make_request(
            'GET',
            '/balances/{currency}/{external_id}'
            .format(currency=currency, external_id=self.get_prefixed_account_id(account_id))
        )['balance']
        if balance.startswith('0x'):
            if balance == '0x':
                return 0
            return int(balance, 16)
        return float(balance)

    def get_balance_by_address(self, address, currency):
        balance = self.make_request(
            'GET',
            '/balances/{currency}/address/{address}'
            .format(currency=currency, address=address)
        )['balance']
        if balance.startswith('0x'):
            if balance == '0x':
                return 0
            return int(balance, 16)
        return float(balance)

    def get_account(self, account_id, currency='BTC'):
        account_data = self.make_request('GET', '/accounts/{external_id}/{currency}'
                                         .format(external_id=self.get_prefixed_account_id(account_id),
                                                 currency=currency))
        account_data['account']['externalId'] = self.remove_prefix_from_account_id(
            account_data['account']['externalId']
        )
        return Account.from_server_response(account_data)

    def get_account_by_address(self, address):
        account_data = self.make_request('GET', '/accounts/{address}'
                                         .format(address=address))
        account_data['account']['externalId'] = self.remove_prefix_from_account_id(
            account_data['account']['externalId']
        )
        return Account.from_server_response(account_data)

    def build_transaction(self, account_id, currency, destination, amount):
        body = {
            "destination": destination,
            "amount": amount,
        }
        return Wallet4Transaction(**self.make_request('POST',
                                                      '/transactions/build/{external_id}/{currency}'
                                                      .format(external_id=self.get_prefixed_account_id(account_id),
                                                              currency=currency),
                                                      body=json.dumps(body)))

    def submit(self, account_id, transaction, currency):
        if not isinstance(transaction, BaseTransaction):
            raise ValueError('transaction should be instance of BaseTransaction class')
        return self.make_request('POST', '/transactions/submit/{external_id}/{currency}'
                                 .format(external_id=self.get_prefixed_account_id(account_id), currency=currency),
                                 body=transaction.to_json())

    def sign_wallet4_transaction(self, transaction, account_id, currency):
        account = self.get_account(account_id, currency)
        return account.sign(transaction, 'OPERATOR', self.secret)

    def cosign_wallet4_and_submit(self, transaction, account_id, currency='BTC'):
        transaction = self.sign_wallet4_transaction(transaction, account_id, currency)
        return self.submit(account_id, transaction, currency)

    def build_recovery_transaction(self, account_id, currency, old_address):
        response = self.make_request(
            'POST',
            '/transactions/build_recovery/{external_id}/{currency}/{address}'
            .format(external_id=self.get_prefixed_account_id(account_id), currency=currency, address=old_address)
        )
        logger.debug('response: {}'.format(response))
        if response.get('account_id'):
            return RecoveryTransaction(response['operator'], response['recovery_transaction'], response['account_id'])
        else:
            return RecoveryTransaction(response['operator'], response['recovery_transaction'],
                                       entropy=response['entropy'],
                                       public_key=response['public_key'],
                                       recovery_address=old_address
                                       )

    def cosign_and_recovery(self, transaction, account_id, currency='BTC'):
        transaction = self.sign_wallet4_transaction(transaction, account_id, currency)
        return self.submit(account_id, transaction, currency)

    def build_grant_transaction(self, account_id, currency, destination, amount, signatures_required):
        body = {
            "destination": destination,
            "amount": str(amount),
            "signatures_required": str(signatures_required),
            "operation_type": "grant"
        }
        transaction = self.make_request('POST',
                                        '/transactions/build/{id}/{currency}'
                                        .format(id=self.get_prefixed_account_id(account_id), currency=currency),
                                        json.dumps(body))
        return GrantTransaction(**transaction)

    def make_request(self, method, uri, body=None):
        url = self.ambisafe_server + uri
        headers = {u'Accept': u'application/json'}
        if method in [u'POST', u'PUT']:
            headers[u'Content-Type'] = u'application/json'
        logger.debug(u'Request to ambisafe KeyServer: method: {}, url: "{}", headers: {}, data: {}'
                     .format(method, url, headers, body))
        response = requests.request(method, url, headers=headers, data=body,
                                    auth=AmbisafeAuth(self.api_key, self.api_secret),
                                    timeout=(self.connect_timeout, self.read_timeout))
        logger.debug(u'Response from ambisafe KeyServer: status: {}, text: {}'
                     .format(response.status_code, response.text))
        return Client._handle_response(response)

    @staticmethod
    def _handle_response(response):
        try:
            response_data = response.json()
        except ValueError as e:
            # ValueError is parent of JSONDecodeError
            raise ServerError(e.message, '')

        if not response.ok:
            if 400 <= response.status_code < 500:
                raise ClientError(response_data['message'], response_data['error'])
            elif 500 <= response.status_code < 600:
                raise ServerError(response_data['message'], response_data['error'])

        return response_data
