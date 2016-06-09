import util
import sys


class Payments:

    def __init__(self):
        return

    class Payment:

        class Authentication:

            def __init__(self, kwargs):
                self.method = util.get_arg(kwargs, 'method')
                self.url = util.get_arg(kwargs, 'url')
                self.params = util.get_arg(kwargs, 'params')

        def __init__(self, kwargs):
            auth = Payments.Payment.Authentication(util.get_arg(kwargs, 'authentication'))
            self.order_id = util.get_arg(kwargs, 'order_id')
            self.txn_id = util.get_arg(kwargs, 'txn_id')
            self.status = util.get_arg(kwargs, 'status')
            self.payment = util.get_arg(kwargs, 'payment')
            self.authentication = auth

    @staticmethod
    def create_card_payment(**kwargs):
        method = 'POST'
        url = '/txns'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['order_id', 'merchant_id', 'payment_method_type', 'card_token', 'card_number', 'name_on_card',
                    'card_exp_year',
                    'card_exp_month', 'card_security_code', 'save_to_locker', 'redirect_after_payment', 'format']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['order_id', 'merchant_id', 'payment_method_type', 'card_token', 'card_number', 'name_on_card',
                    'card_exp_year',
                    'card_exp_month', 'card_security_code', 'save_to_locker', 'redirect_after_payment', 'format']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Payments.create_card_payment()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['order_id', 'merchant_id', 'payment_method_type', 'payment_method', 'card_token',
                           'name_on_card',
                           'card_number', 'card_exp_year', 'card_exp_month', 'card_security_code', 'save_to_locker',
                           'redirect_after_payment', 'format']:
                sys.stderr.write('%s not a valid argument for Payments.create_card_payment()\n' % key)

        # Type checks
        for key, value in kwargs.iteritems():
            if key == 'save_to_locker':
                if type(parameters['save_to_locker']) is not bool:
                    sys.stderr.write('save_to_locker should be of type bool\n')
            if key == 'redirect_after_payment':
                if type(parameters['redirect_after_payment']) is not bool:
                    sys.stderr.write('redirect_after_payment should be of type bool\n')

        response = util.request(method, url, parameters).json()
        payment = Payments.Payment(response)
        return payment

    @staticmethod
    def create_net_banking_payment(**kwargs):
        method = 'POST'
        url = '/txns'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['order_id', 'merchant_id', 'payment_method_type', 'payment_method', 'redirect_after_payment',
                    'format']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['order_id', 'merchant_id', 'payment_method_type', 'payment_method', 'redirect_after_payment',
                    'format']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Payments.create_net_banking_payment()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['order_id', 'merchant_id', 'payment_method_type', 'payment_method', 'redirect_after_payment',
                           'format']:
                sys.stderr.write('%s not a valid argument for Payments.create_net_banking_payment()\n' % key)

        response = util.request(method, url, parameters).json()
        payment = Payments.Payment(response)
        return payment
