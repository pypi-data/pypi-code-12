from functools import partial
import logging
import json
from .containers import Container

logger = logging.getLogger('ambisafe')


class Account(object):
    @classmethod
    def from_server_response(cls, response):
        """Creates Account subclass for corresponding security schema from response from Ambisafe KeyServer
        :param response:
        :type response: dict
        :returns: Account -- Account subclass
        """
        logger.debug('Ambisafe.account.Account.from_server_response | creating account from response: {}'
                     .format(response))
        account_id = response['account']['externalId']
        security_schema = response['account']['securitySchemaName']
        address = response['account']['address']

        if security_schema in ('Wallet4', 'Wallet4v2'):
            containers = {}
            for role, container in response.get('containers', {}).items():
                try:
                    del container['role']
                except KeyError:
                    pass
                containers[role] = Container.from_server_response(**container)
            if security_schema == 'Wallet4':
                version = 1
            else:
                version = 2
            return Wallet4Account(account_id, user_container=containers['USER'],
                                  operator_container=containers['OPERATOR'],
                                  address=address, version=version)
        elif security_schema in ['Simple', 'SimpleMultisig']:
            return SimpleAccount(account_id, address)
        elif security_schema == 'MasterWallet':
            return MasterWalletAccount(account_id, response['containers'], address=address)
        elif security_schema == 'UserSideKey':
            container = response.get('containers', {})['USER']
            try:
                del container['role']
            except KeyError:
                pass
            user_container = Container.from_server_response(**container)
            return UserSideKeyAccount(account_id, user_container=user_container, address=address)
        else:
            raise NotImplementedError('This security schema is not implemented')

    def as_dict(self):
        """Returns dict representations of account
        :return: dict
        """
        raise NotImplemented

    def to_json(self):
        """Returns json representations of account
        :return: str
        """
        return json.dumps(self.as_dict())

    @property
    def security_schema(self):
        return self._security_schema

    def __repr__(self):
        return '<Account id={} schema={} address={}>'.format(self.id, self._security_schema, self.address)


class SimpleAccount(Account):
    def __init__(self, account_id, address=None, currency='BTC'):
        """Base account class
        :param account_id: ID of account
        :type account_id: int or basestring
        :param address:
        :type address: basestring
        :param currency:
        :type currency: basestring
        :return:
        """
        self.id = account_id
        self.currency = currency
        self.address = address
        self._security_schema = 'Simple'

    def as_dict(self):
        """Returns dict representations of account
        :return: dict
        """
        return {
            'id': self.id,
            'currency': self.currency,
            'security_schema': self._security_schema,
        }


class UserSideKeyAccount(Account):
    def __init__(self, account_id, user_container=None, address=None, currency='BTC'):
        assert isinstance(user_container, Container)
        self.user_container = user_container
        self.id = account_id
        self.currency = currency
        self.address = address
        self._security_schema = 'UserSideKey'

    def as_dict(self):
        """Returns dict representation of account
        :return: dict
        """
        return {
            'id': self.id,
            'currency': self.currency,
            'security_schema': self._security_schema,
            'containers': {
                'USER': self.user_container,
            },
        }

    def sign(self, transaction, secret):
        private_key = self.user_container.get_private_key(secret)
        sign = partial(self.user_container.sign, private_key=private_key)
        signed_sighashes = map(sign, transaction.sighashes)
        transaction.user_signatures = signed_sighashes
        return transaction


class Wallet4Account(Account):
    def __init__(self, account_id, operator_container=None,
                 user_container=None, address=None, currency='BTC',
                 version=1):
        """Creates Wallet4 account object
        :param account_id:
        :type account_id: basestring or int
        :param operator_container:
        :type operator_container: Container
        :param user_container:
        :type user_container: Container
        :param address:
        :type address: basestring
        :param currency:
        :type currency: basestring
        :return:
        """
        assert isinstance(user_container, Container)
        assert isinstance(operator_container, Container)
        self.user_container = user_container
        self.operator_container = operator_container
        self.id = account_id
        self.currency = currency
        self.address = address
        if version == 1:
            self._security_schema = 'Wallet4'
        elif version == 2:
            self._security_schema = 'Wallet4v2'
        else:
            raise ValueError('Wrong Wallet4 version')

    def as_dict(self):
        """Returns dict representations of account
        :return: dict
        """
        return {
            'id': self.id,
            'currency': self.currency,
            'security_schema': self._security_schema,
            'containers': {
                'USER': self.user_container,
                'OPERATOR': self.operator_container,
            },
        }

    def sign(self, transaction, container_name, secret):
        if container_name == 'USER':
            container = self.user_container
        elif container_name == 'OPERATOR':
            container = self.operator_container
        else:
            raise ValueError('container_name should be "USER" or "OPERATOR"')

        private_key = container.get_private_key(secret)
        sign = partial(container.sign, private_key=private_key)
        signed_sighashes = map(sign, transaction.sighashes)

        if container_name == 'USER':
            transaction.user_signatures = signed_sighashes
        elif container_name == 'OPERATOR':
            transaction.operator_signatures = signed_sighashes

        return transaction


class MasterWalletAccount(Account):
    def __init__(self, account_id, containers, address, currency=None):
        self._security_schema = 'MasterWallet'
        self.account_id = account_id
        self.address = address
        self.containers = containers
        self.currency = currency

    def sign(self, transaction, container_number, secret):
        container = self.containers[str(container_number)]
        private_key = container.get_private_key(secret)
        sign = partial(container.sign, private_key=private_key)
        signed_sighashes = map(sign, transaction.sighashes)
        transaction.add_signature(container_number, signed_sighashes)

    def __repr__(self):
        return '<Account id={} schema={} address={}>'.format(self.account_id, self._security_schema, self.address)
