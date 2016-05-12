from __future__ import absolute_import

# import models into sdk package
from .models.account import Account
from .models.alias import Alias
from .models.balance import Balance
from .models.create_account_request import CreateAccountRequest
from .models.create_account_response import CreateAccountResponse
from .models.create_alias_request import CreateAliasRequest
from .models.create_alias_token_request import CreateAliasTokenRequest
from .models.create_alias_token_response import CreateAliasTokenResponse
from .models.create_device_request import CreateDeviceRequest
from .models.create_device_response import CreateDeviceResponse
from .models.create_member_request import CreateMemberRequest
from .models.create_member_request_device import CreateMemberRequestDevice
from .models.create_member_response import CreateMemberResponse
from .models.create_member_response_device import CreateMemberResponseDevice
from .models.create_payment_request import CreatePaymentRequest
from .models.create_payment_response import CreatePaymentResponse
from .models.create_token_request import CreateTokenRequest
from .models.currency_unit import CurrencyUnit
from .models.get_account_response import GetAccountResponse
from .models.get_accounts_response import GetAccountsResponse
from .models.get_alias_response import GetAliasResponse
from .models.get_aliases_response import GetAliasesResponse
from .models.get_device_response import GetDeviceResponse
from .models.get_devices_response import GetDevicesResponse
from .models.get_devices_response_device import GetDevicesResponseDevice
from .models.get_token_response import GetTokenResponse
from .models.get_tokens_response import GetTokensResponse
from .models.get_transactions_response import GetTransactionsResponse
from .models.get_transactions_response_transaction import GetTransactionsResponseTransaction
from .models.math_context import MathContext
from .models.money import Money
from .models.payment_request import PaymentRequest
from .models.proxy_payment_response import ProxyPaymentResponse
from .models.system_check_response import SystemCheckResponse
from .models.system_information_response import SystemInformationResponse
from .models.system_information_response_dependency import SystemInformationResponseDependency
from .models.system_state_response import SystemStateResponse
from .models.system_state_response_property import SystemStateResponseProperty
from .models.token import Token
from .models.token_request import TokenRequest
# import models into sdk package
from .models.authority import Authority
from .models.big_int import BigInt
from .models.big_integer import BigInteger
from .models.create_access_request import CreateAccessRequest
from .models.create_access_response import CreateAccessResponse
from .models.create_subscription_request import CreateSubscriptionRequest
from .models.create_subscription_response import CreateSubscriptionResponse
from .models.create_transfer_request import CreateTransferRequest
from .models.create_transfer_response import CreateTransferResponse
from .models.currency_unit import CurrencyUnit
from .models.get_access_response import GetAccessResponse
from .models.get_access_response_balance import GetAccessResponseBalance
from .models.get_access_response_property import GetAccessResponseProperty
from .models.get_subscriptions_response import GetSubscriptionsResponse
from .models.get_subscriptions_response_subscription import GetSubscriptionsResponseSubscription
from .models.get_transactions_response import GetTransactionsResponse
from .models.get_transactions_response_transaction import GetTransactionsResponseTransaction
from .models.host import Host
from .models.math_context import MathContext
from .models.money import Money
from .models.path import Path
from .models.query import Query
from .models.system_check_response import SystemCheckResponse
from .models.system_information_response import SystemInformationResponse
from .models.system_information_response_dependency import SystemInformationResponseDependency
from .models.system_state_response import SystemStateResponse
from .models.system_state_response_property import SystemStateResponseProperty
from .models.uri import Uri
from .models.verify_access_request import VerifyAccessRequest

# import models into sdk package
from .models.create_alias_request import CreateAliasRequest
from .models.create_alias_response import CreateAliasResponse
from .models.function1_request_context_boxed_unit import Function1RequestContextBoxedUnit
from .models.get_alias_response import GetAliasResponse
from .models.system_check_response import SystemCheckResponse
from .models.system_information_response import SystemInformationResponse
from .models.system_information_response_dependency import SystemInformationResponseDependency
from .models.system_state_response import SystemStateResponse
from .models.system_state_response_property import SystemStateResponseProperty

# import apis into sdk package
from .apis.combined_provider_api import CombinedProviderApi as CPA
from .apis.combined_bank_api import CombinedBankApi as CBA
from .apis.combined_aliases_api import CombinedAliasesApi as CAA

import ed25519
import datetime
import json
from urllib.parse import quote
import codecs
import uuid
import os
from hashlib import sha256
import binascii

def welcome_message():
    print("Welcome to the Token console. Type Token.help() for help.")

def help():
    print("+-------------------------------------------------------------+")
    print("| Welcome to the Token console. Here we can issue commands to |")
    print("| interact with the Token system. Please know that the system |")
    print("| is still in development and therefore there will be bugs/   |")
    print("| missing pieces                                              |")
    print("+-------------------------------------------------------------+")
    print("| KEYS                                                        |")
    print("| In order to execute some of these commands, you will need   |")
    print("| specific private keys. Please ask a Token employee to       |")
    print("| obtain these                                                |")
    print("+-------------------------------------------------------------+")
    print("| COMMANDS - Token                                            |")
    print("| Token.ProviderService(provider_code)                        |")
    print("| Token.BankService(provider_code)                            |")
    print("| Token.create_keypair()                                      |")
    print("| Token.set_context(context, key)                             |")
    print("| Token.demo(1)                      // show demo (1)         |")
    print("| Token.help()                       // print this            |")
    print("+-------------------------------------------------------------+")
    print("| COMMANDS - Bank Service                                     |")
    print("| create_access(client, account, provider_code, session_id)   |")
    print("+-------------------------------------------------------------+")
    print("| COMMANDS - Provider Service                                 |")
    print("| create_member(device_name, push_notif_id, pk)               |")
    print("| create_alias(alias, description='')                         |")
    print("| create_account(bank_code, access_id, name)                  |")
    print("| get_account(account_id)                                     |")
    print("| get_accounts()                                              |")
    print("| create_token(alias, description='', terms='')               |")
    print("| get_token(token_id)                                         |")
    print("| get_tokens()                                                |")
    print("| endorse_token(token_id, account_id)                         |")
    print("| get_transactions(account_id)                                |")
    print("| create_payment(token_id, acc_id, value, unit, description=''|")
    print("|      protocol='', destination='')                           |")
    print("+-------------------------------------------------------------+")
    print("| You can use dir(object) to see what methods its has.        |")
    print("+-------------------------------------------------------------+")

class ProviderService(CPA):
    def __init__(self, provider_code, env_arg=''):
        self.provider_code = provider_code
        if env == 'dev' or env=='local':
            self.host = 'http://' + provider_code + '.provider.dev.api.token.io:80'
        elif env == 'stg':
            self.host = 'http://' + provider_code + '.provider.stg.api.token.io:80'
        elif env == 'prod':
            self.host = 'http://' + provider_code + '.provider.prd.api.token.io:80'
        if env_arg == 'dev' or env_arg=='local':
            self.host = 'http://' + provider_code + '.provider.dev.api.token.io:80'
        elif env_arg == 'prod':
            self.host = 'http://' + provider_code + '.provider.prd.api.token.io:80'
        elif env_arg == 'stg':
            self.host = 'http://' + provider_code + '.provider.stg.api.token.io:80'
        super(ProviderService, self).__init__(self.host)
    def extra(self):
        print("extra")
    def create_member(self, device_name, push_id, pk):
        request = {'device': {'name':device_name, 'pushNotificationId':push_id, \
            'publicKeys':[pk]}}
        member = self.create_member_route(request)
        member.provider = self.provider_code
        return member
    def create_alias(self, alias_code, description=''):
        request = {'description':description}
        auth = create_authorization('POST', self.host + '/aliases/' + \
        alias_code, request)
        return self.create_alias_route(alias_code, request, authorization=auth)
    def get_accounts(self):
        auth = create_authorization('GET', self.host + '/accounts')
        return self.get_accounts_route(authorization=auth)
    def get_account(self, account_id):
        auth = create_authorization('GET', self.host + '/accounts/' + \
            quote(account_id))
        return self.get_account_route(account_id, authorization=auth)
    def create_account(self, bank_code, access_id, name):
        request = {
          "bankCode": bank_code,
          "accessId": access_id,
          "name": name
        }
        auth = create_authorization('POST', self.host + '/accounts',
            request)
        return self.create_account_route(request, authorization=auth)
    def get_tokens(self):
        auth = create_authorization('GET', self.host + '/tokens?pageOffset=0&pageLimit=100')
        return self.get_tokens_route(authorization=auth)
    def get_token(self, token_id):
        auth = create_authorization('GET', self.host + '/tokens/' + \
            quote(token_id))
        return self.get_token_route(token_id, authorization=auth)
    def create_token(self, alias, description='', terms=''):
        request = {
          "payerAliasCode": alias,
          "description": description,
          "terms": terms
        }
        auth = create_authorization('POST', self.host + '/tokens', request)
        return self.create_alias_token_route(request, authorization=auth)
    def endorse_token(self, token_id, acc_id):
        request = { 'accountId':acc_id }
        auth = create_authorization('PUT', self.host + '/tokens/' + \
        quote(token_id) + '/endorse', request)
        return self.endorse_token_route(token_id, request, authorization=auth)
    def decline_token(self, token_id):
        auth = create_authorization('PUT', self.host + '/tokens/' + \
        quote(token_id) + '/decline')
        return self.decline_token_route(token_id, authorization=auth)
    def create_payment(self, token_id, acc_id, value, unit, description='',
        protocol='', destination=''):
        request = {
          "accountId": acc_id,
          "description": description,
          "amount": {
            "value": str(value),
            "unit": unit
          },
          "protocol": protocol,
          "destination": destination
        }
        auth = create_authorization('POST', self.host + '/tokens/' + \
        quote(token_id) + '/payments', request)
        return self.create_payment_route(token_id, request, authorization=auth)
    def get_transactions(self, account_id):
        auth = create_authorization('GET', self.host + '/accounts/' + \
        quote(account_id) + '/transactions?pageOffset=0&pageLimit=100')
        return self.get_transactions_route(account_id, 0, 100, authorization=auth)



class BankService(CBA):
    def __init__(self, bank_code, env_arg=''):
        if env == 'dev' or env=='local':
            self.host = 'http://' + bank_code + '.bank.dev.api.token.io:80'
        elif env == 'stg':
            self.host = 'http://' + bank_code + '.bank.stg.api.token.io:80'
        elif env == 'prod':
            self.host = 'http://' + bank_code + '.bank.prd.api.token.io:80'
        if env_arg == 'dev' or env_arg=='local':
            self.host = 'http://' + bank_code + '.bank.dev.api.token.io:80'
        elif env_arg == 'prod':
            self.host = 'http://' + bank_code + '.bank.prd.api.token.io:80'
        elif env_arg == 'stg':
            self.host = 'http://' + bank_code + '.bank.stg.api.token.io:80'
        super(BankService, self).__init__(self.host)
    def extra(self):
        print("extra")
    def create_access(self, client, account, provider_code, session_id='test'):
        request = {
          'sessionId': session_id,
          'providerCode': provider_code,
        }
        auth = create_authorization('POST', self.host + '/clients/' +
            client + '/accounts/' + account + '/accesses', request)
        return self.create_access_route(client, account, request, authorization=auth)
    # def verify_access(self, access_id, request):
    #     auth = create_authorization('PUT', 'http://bank.dev.api.token.io:80/accesses/' +
    #         quote(access_id) + '/verify', request)
    #     return self.verify_access_route(access_id, request, authorization=auth)

class AliasService(CAA):
    def __init__(self, env_arg=''):
        if env == 'dev' or env=='local':
            self.host = 'http://alias.dev.api.token.io:80'
        elif env == 'stg':
            self.host = 'http://alias.stg.api.token.io:80'
        elif env == 'prod':
            self.host = 'http://alias.prd.api.token.io:80'
        if env_arg == 'dev' or env_arg=='local':
            self.host = 'http://alias.dev.api.token.io:80'
        elif env_arg == 'prod':
            self.host = 'http://alias.prd.api.token.io:80'
        elif env_arg == 'stg':
            self.host = 'http://alias.stg.api.token.io:80'
        super(AliasService, self).__init__(self.host)
    def get_alias(self, alias):
        m = sha256()
        m.update(alias.encode())
        base = binascii.b2a_base64(m.digest())
        no_padding = (base.decode('utf-8')).split('=')[0]
        replace1 = no_padding.replace('+', '-')
        replace2 = replace1.replace('/', '_')
        auth = create_authorization('GET', self.host + '/aliases/' +
            replace2)
        return self.get_alias_route(replace2, authorization=auth)

context = {
    'subject_id':'',
    'sk': '',
    }
try:
    with open('config.json') as json_data_file:
        json_data = json.load(json_data_file)
        env = json_data["environment"]
        keys = json_data["keys"][env]
except FileNotFoundError:
    print("In order to use Token, you need a config.json file in this directory. Please contact a Token developer")


def demo(demo_num):
    script_path = os.path.dirname(os.path.abspath( __file__ ))
    try:
        f = open(os.path.join(script_path,'demos/' + env + '-demo' + str(demo_num) + '.py'))
        print(f.read())
    except IOError:
        print("Demo does not exist.")

def create_authorization(method='GET', url='/', body=None, iso_date=None, nonce=None):
    subject_id = context["subject_id"]
    subject_sk = context["sk"]

    if not iso_date:
        iso_date = datetime.datetime.utcnow().isoformat()[:23] + 'Z'
    if not nonce:
        while nonce is None or nonce[0] == '0':
            nonce = str(ed25519.create_keypair()[0].to_ascii(encoding='hex'), encoding='UTF-8')


    index0 = url.index('/')
    index1 = url.index('/', index0 + 1)
    index2 = url.index('/', index1 + 1)
    path_and_query = url[index2:]
    path = path_and_query
    and_query = ""

    if '?' in path_and_query:
        index3 = path_and_query.index('?')
        path = path_and_query[0:index3]
        sorted_query = path_and_query[index3 + 1:]
        sorted_query = "&".join(sorted(sorted_query.split('&')))
        and_query = "?" + sorted_query

    andd = " "
    anddBody = ""

    if body is not None and body != '':
        anddBody = andd + json.dumps(body, sort_keys=True, separators=(',',':'))

    payload = subject_id + andd + iso_date + andd + nonce + andd + method + andd \
        + path + and_query + anddBody;

    key = ed25519.SigningKey(ed25519.keys.from_ascii(context["sk"], encoding="hex"))
    signature = str(codecs.encode(key.sign(str.encode(payload)), 'hex'), encoding="UTF-8")

    comma = ','

    credentials = "subject-id=" + quote(subject_id) + comma + \
        "request-timestamp=" + quote(iso_date) + comma + \
        "request-nonce=" + nonce + comma + \
        "request-signature=" + signature

    scheme = "Token-Ed25519-SHA512"
    return scheme + andd + credentials

def create_keypair():
    sk, vk = ed25519.create_keypair()
    return str(sk.to_ascii(encoding="hex"), encoding='UTF-8'), str(vk.to_ascii(encoding="hex"), encoding='UTF-8')

def set_context(data, sk):
    global context
    if hasattr(data, 'device'):
        subject_id = "provider-" + data.provider + "-member-" + data.id + "-device-" + data.device.id
    else:
        subject_id = data
    context = {
        'subject_id': subject_id,
        'sk': sk,
        }


# import ApiClient
from .api_client import ApiClient

from .configuration import Configuration


configuration = Configuration()
welcome_message()
