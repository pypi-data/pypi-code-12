import util
import sys


class Cards:

    def __init__(self):
        return

    class Card:

        def __init__(self, kwargs):
            self.name = util.get_arg(kwargs, 'name_on_card')
            self.exp_year = util.get_arg(kwargs, 'card_exp_year')
            self.reference = util.get_arg(kwargs, 'card_reference')
            self.exp_month = util.get_arg(kwargs, 'card_exp_month')
            self.expired = util.get_arg(kwargs, 'expired')
            self.fingerprint = util.get_arg(kwargs, 'card_fingerprint')
            self.isin = util.get_arg(kwargs, 'card_isin')
            self.type = util.get_arg(kwargs, 'card_type')
            self.issuer = util.get_arg(kwargs, 'card_issuer')
            self.brand = util.get_arg(kwargs, 'card_brand')
            self.token = util.get_arg(kwargs, 'card_token')
            self.nickname = util.get_arg(kwargs, 'nickname')
            self.number = util.get_arg(kwargs, 'card_number')
            self.deleted = util.get_arg(kwargs, 'deleted')

    @staticmethod
    def add(**kwargs):

        method = 'POST'
        url = '/card/add'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['merchant_id', 'customer_id', 'customer_email', 'card_number', 'card_exp_year', 'card_exp_month']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['merchant_id', 'customer_id', 'customer_email', 'card_number', 'card_exp_year', 'card_exp_month']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Cards.add()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['merchant_id', 'customer_id', 'customer_email', 'card_number', 'card_exp_year',
                           'card_exp_month', 'name_on_card', 'nickname']:
                sys.stderr.write('%s not a valid argument for Cards.add()\n' % key)

        response = util.request(method, url, parameters).json()
        card = Cards.Card(response)
        return card

    @staticmethod
    def list(**kwargs):

        method = 'GET'
        url = '/card/list'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['customer_id']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['customer_id']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Cards.list()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['customer_id']:
                sys.stderr.write('%s not a valid argument for Cards.list()\n' % key)

        response = util.request(method, url, parameters).json()
        response = util.get_arg(response,'cards')
        cards = []
        if response is not None:
            for card in response:
                card = Cards.Card(card)
                cards.append(card)
        return cards

    @staticmethod
    def delete(**kwargs):
        method = 'POST'
        url = '/card/delete'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['card_token']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['card_token']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Cards.delete()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['card_token']:
                sys.stderr.write('%s not a valid argument for Cards.delete()\n' % key)

        response = util.request(method, url, parameters).json()
        card = Cards.Card(response)
        return card

    @staticmethod
    def get_fingerprint(**kwargs):
        method = 'POST'
        url = '/card/fingerprint'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['card_number']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['card_number']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Cards.get_fingerprint()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['card_number']:
                sys.stderr.write('%s not a valid argument for Cards.get_fingerprint()\n' % key)

        fingerprint = util.request(method, url, parameters).json()['card_fingerprint']
        return fingerprint
