import util
import sys
from Cards import Cards


class Orders:

    def __init__(self):
        return

    all_input_params = ['order_id', 'amount', 'currency', 'customer_id', 'customer_email', 'customer_phone',
                        'description', 'product_id', 'gateway_id', 'return_url', 'billing_address_first_name',
                        'billing_address_last_name', 'billing_address_line1', 'billing_address_line2',
                        'billing_address_line3', 'billing_address_city', 'billing_address_state',
                        'billing_address_country', 'billing_address_postal_code', 'billing_address_phone',
                        'billing_address_country_code_iso', 'shipping_address_first_name',
                        'shipping_address_last_name', 'shipping_address_line1', 'shipping_address_line2',
                        'shipping_address_line3', 'shipping_address_city', 'shipping_address_state',
                        'shipping_address_country', 'shipping_address_postal_code', 'shipping_address_phone',
                        'shipping_address_country_code_iso', 'udf1', 'udf2', 'udf3', 'udf4', 'udf5', 'udf6', 'udf7',
                        'udf8', 'udf9', 'udf10']

    class Order:

        class Address:

            def __init__(self, address_type, kwargs):
                self.type = address_type
                self.first_name = util.get_arg(kwargs, self.type + '_address_first_name')
                self.last_name = util.get_arg(kwargs, self.type + '_address_last_name')
                self.line1 = util.get_arg(kwargs, self.type + '_address_line1')
                self.line2 = util.get_arg(kwargs, self.type + '_address_line2')
                self.line3 = util.get_arg(kwargs, self.type + '_address_line3')
                self.city = util.get_arg(kwargs, self.type + '_address_city')
                self.state = util.get_arg(kwargs, self.type + '_address_state')
                self.country = util.get_arg(kwargs, self.type + '_address_country')
                self.postal_code = util.get_arg(kwargs, self.type + '_address_postal_code')
                self.phone = util.get_arg(kwargs, self.type + '_address_phone')
                self.country_code_iso = util.get_arg(kwargs, self.type + '_address_country_code_iso')

        class Refund:

                def __init__(self, kwargs):
                    self.id = util.get_arg(kwargs, 'refund_id')
                    self.ref = util.get_arg(kwargs, 'ref')
                    self.amount = util.get_arg(kwargs, 'amount')
                    self.created = util.get_arg(kwargs, 'created')
                    self.status = util.get_arg(kwargs, 'status')

        class GatewayResponse:

                def __init__(self, kwargs):
                    self.rrn = util.get_arg(kwargs, 'rrn')
                    self.epg_txn_id = util.get_arg(kwargs, 'epg_txn_id')
                    self.auth_id_code = util.get_arg(kwargs, 'auth_id_code')
                    self.txn_id = util.get_arg(kwargs, 'txn_id')
                    self.resp_code = util.get_arg(kwargs, 'resp_code')
                    self.resp_message = util.get_arg(kwargs, 'resp_message')

        def __init__(self, kwargs):

            billing_address = Orders.Order.Address("billing", kwargs)
            shipping_address = Orders.Order.Address("shipping", kwargs)
            card = Cards.Card(util.get_arg(kwargs, 'card'))
            gateway_response = Orders.Order.GatewayResponse(util.get_arg(kwargs, 'payment_gateway_response'))
            refunds = []
            if 'refunds' in kwargs:
                for refund in kwargs['refunds']:
                    refund_obj = Orders.Order.Refund(refund)
                    refunds.append(refund_obj)
            self.merchant_id = util.get_arg(kwargs, 'merchant_id')
            self.order_id = util.get_arg(kwargs, 'order_id')
            self.status = util.get_arg(kwargs, 'status')
            self.status_id = util.get_arg(kwargs, 'status_id')
            self.amount = util.get_arg(kwargs, 'amount')
            self.currency = util.get_arg(kwargs, 'currency')
            self.customer_id = util.get_arg(kwargs, 'customer_id')
            self.customer_email = util.get_arg(kwargs, 'customer_email')
            self.customer_phone = util.get_arg(kwargs, 'customer_phone')
            self.product_id = util.get_arg(kwargs, 'product_id')
            self.return_url = util.get_arg(kwargs, 'return_url')
            self.description = util.get_arg(kwargs, 'description')
            self.billing_address = billing_address
            self.shipping_address = shipping_address
            self.udf1 = util.get_arg(kwargs, 'udf1')
            self.udf2 = util.get_arg(kwargs, 'udf2')
            self.udf3 = util.get_arg(kwargs, 'udf3')
            self.udf4 = util.get_arg(kwargs, 'udf4')
            self.udf5 = util.get_arg(kwargs, 'udf5')
            self.udf6 = util.get_arg(kwargs, 'udf6')
            self.udf7 = util.get_arg(kwargs, 'udf7')
            self.udf8 = util.get_arg(kwargs, 'udf8')
            self.udf9 = util.get_arg(kwargs, 'udf9')
            self.udf10 = util.get_arg(kwargs, 'udf10')
            self.txn_id = util.get_arg(kwargs, 'txn_id')
            self.gateway_id = util.get_arg(kwargs, 'gateway_id')
            self.bank_error_code = util.get_arg(kwargs, 'bank_error_code')
            self.bank_error_message = util.get_arg(kwargs, 'bank_error_message')
            self.refunded = util.get_arg(kwargs, 'refunded')
            self.amount_refunded = util.get_arg(kwargs, 'amount_refunded')
            self.card = card
            self.gateway_response = gateway_response
            self.refunds = refunds

    @staticmethod
    def create(**kwargs):

        method = 'POST'
        url = '/order/create'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['order_id', 'amount']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['order_id', 'amount']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Order.create()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in Orders.all_input_params:
                sys.stderr.write('%s not a valid argument for Order.create()\n' % key)
        response = util.request(method, url, parameters).json()

        # Type checks
        if type(parameters['amount']) is not float and type(parameters['amount']) is not int:
            sys.stderr.write('amount should be of type float or int\n')
        order = Orders.Order(response)
        return order

    @staticmethod
    def get_status(**kwargs):

        method = 'GET'
        url = '/order/status'
        required_args = {}
        parameters = {}

        # required_args checks for presence of necessary parameters
        for key in ['order_id']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['order_id']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Orders.get_status()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['order_id']:
                sys.stderr.write('%s not a valid argument for Orders.get_status()\n' % key)

        response = util.request(method, url, parameters).json()
        order = Orders.Order(response)
        return order

    @staticmethod
    def list(**kwargs):

        method = 'GET'
        url = '/order/list'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in []:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in []:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Orders.list()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['created.gt', 'created.lt', 'created.ge', 'created.le', 'count', 'offset']:
                sys.stderr.write('%s not a valid argument for Orders.list()\n' % key)

        # Type checks
        for key, value in kwargs.iteritems():
            if key == 'created.gt':
                if type(parameters['created.gt']) is not int:
                    sys.stderr.write('created.gt should be of type int\n')
            if key == 'created.lt':
                if type(parameters['created.lt']) is not int:
                    sys.stderr.write('lt should be of type int\n')
            if key == 'created.ge':
                if type(parameters['created.ge']) is not int:
                    sys.stderr.write('created.ge should be of type int\n')
            if key == 'created.le':
                if type(parameters['created.le']) is not int:
                    sys.stderr.write('created.le should be of type int\n')
            if key == 'count':
                if type(parameters['count']) is not int:
                    sys.stderr.write('count should be of type int\n')
            if key == 'offset':
                if type(parameters['offset']) is not int:
                    sys.stderr.write('offset should be of type int\n')

        response = util.request(method, url, parameters).json()
        orders = []
        for i in xrange(1, response['count']):
            order = Orders.Order(response['list'][i])
            orders.append(order)
        return orders

    @staticmethod
    def update(**kwargs):

        method = 'POST'
        url = '/order/create'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['order_id']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['order_id']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Orders.update()\n' % key)

        # Warn user about unchangeable parameters
        for key, value in kwargs.iteritems():
            if key == 'currency':
                sys.stderr.write('currency cannot be changed\n')
            if key == 'customer_id':
                sys.stderr.write('customer_id cannot be changed\n')
            if key == 'customer_email':
                sys.stderr.write('customer_email cannot be changed\n')
            if key == 'customer_phone':
                sys.stderr.write('customer_phone cannot be changed\n')
            if key == 'description':
                sys.stderr.write('description cannot be changed\n')
            if key == 'product_id':
                sys.stderr.write('product_id cannot be changed\n')
            if key == 'return_url':
                sys.stderr.write('return_url cannot be changed\n')

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in Orders.all_input_params:
                sys.stderr.write('%s not a valid argument for Orders.update()\n' % key)

        response = util.request(method, url, parameters).json()
        order = Orders.Order(response)
        return order

    @staticmethod
    def refund(**kwargs):

        method = 'POST'
        url = '/order/refund'
        parameters = {}

        # required_args checks for presence of necessary parameters
        required_args = {}
        for key in ['unique_request_id', 'order_id']:
            required_args[key] = False

        for key, value in kwargs.iteritems():
            parameters[key] = value
            required_args[key] = True

        # Warn user about missing necessary parameters
        for key in ['unique_request_id', 'order_id']:
            if required_args[key] is False:
                raise Exception('%s is a required argument for Orders.refund()\n' % key)

        # Warn user about unhandled parameters
        for key in parameters:
            if key not in ['unique_request_id', 'order_id', 'amount']:
                sys.stderr.write('%s not a valid argument for Orders.refund()\n' % key)

        response = util.request(method, url, parameters).json()
        order = Orders.Order(response)
        return order
