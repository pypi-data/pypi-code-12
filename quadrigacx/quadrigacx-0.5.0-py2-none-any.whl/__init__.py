from collections import Iterable
from lobgect import log
from auth import Auth
import random

logger = log.Log(__name__)

@logger.log_variables
def check_list_value(unchecked_value, checked_base_object=[], known_good_options=[]):
    logger.debug('The unchecked value is \'{}\''.format(unchecked_value))
    checked_value = list(checked_base_object)
    unchecked_list = list(checked_base_object)

    if not unchecked_value:
        unchecked_list = known_good_options
    elif type(unchecked_value) is not list:
        unchecked_list = unchecked_value.split(',')
    else:
        unchecked_list = unchecked_value

    for unchecked_list_value in unchecked_list:
        if not unchecked_list_value or unchecked_list_value not in known_good_options:
            logger.warn('{} \'{}\' is not a known good value for this parameter'.format(type(unchecked_value), unchecked_value))
        else:
            checked_value.append(unchecked_list_value)

    logger.debug('The checked value is {}'.format(checked_value))

    if len(checked_value) > 0:
        return checked_value
    else:
        logger.warn('None of these values were any good, so you get all the right ones instead.')
        return known_good_options

@logger.log_variables
def check_value(unchecked_value, checked_base_object=None, default_value=None, known_good_options=[], expected_type=None):
    logger.debug('The unchecked value is \'{}\''.format(unchecked_value))
    checked_value = checked_base_object

    # Make sure the input is a good known value
    if not unchecked_value or (known_good_options and unchecked_value not in known_good_options):
        logger.warn('{} \'{}\' is not a known good value for this parameter'.format(type(unchecked_value), unchecked_value))
        checked_value = default_value
        logger.info('The parameter has instead been set as the default of \'{}\''.format(checked_value))

    # Or at least the right type
    elif expected_type:
        if type(unchecked_value) == expected_type:
            checked_value = unchecked_value
        else:  # If the input isn't the right type yet
            if expected_type == bool:
                logger.info("Boolean values can't be coerced from a string, exactly")
                checked_value = True if unchecked_value in ['true', 'True', '1', 't'] else False
            else:
                try:
                    expected_type(unchecked_value)  # try to coerce it
                    checked_value = unchecked_value # We need the string version for the API though
                except ValueError:  # Or ignore it
                    logger.warn('{} \'{}\' is not a known good value for this parameter'.format(type(unchecked_value), unchecked_value))
                    checked_value = default_value
                    logger.info('The parameter has instead been set as the default of \'{}\''.format(checked_value))

    else: checked_value = unchecked_value

    logger.debug('The checked value is \'{}\''.format(checked_value))

    return checked_value

class QCX(object):
    def __init__(self, config_filepath=None, credentials=None):
        self.logger = log.Log(__name__)

        if config_filepath or credentials:
            self.auth = Auth(config_filepath=config_filepath, credentials=credentials)

    def methods(self):
        return {
            'public': [
                {
                    'name':'ticker',
                    'requires': {
                        'book_list': [value for key,value in self.enumerations('order_books').iteritems()]
                    },
                    'optional': {},
                    'returns': {
                        'btc_cad': {
                            u'ask': u'850.99',
                            u'bid': u'837.51',
                            u'high': u'854.62',
                            u'last': u'850.99',
                            u'low': u'836.01',
                            u'timestamp': u'1467251546',
                            u'volume': u'242.77034781',
                            u'vwap': u'833.81'
                        }
                    },
                },
                {
                    'name':'order_book',
                    'requires':{
                        'book_list': [value for key,value in self.enumerations('order_books').iteritems()]
                    },
                    'optional':{
                        'group_transactions': self.enumerations('group_transactions')[random.choice(self.enumerations('group_transactions').keys())]
                    },
                    'returns':{
                        'eth_btc': {
                            u'asks': [
                                [u'0.02050000', u'3.95121952'],
                                [u'0.02060000', u'5.00000000'],
                                [u'4879.00000000', u'0.28791201']
                            ],
                            u'bids': [
                                [u'0.00550000', u'200.00000000'],
                                [u'0.00510000', u'250.00000000'],
                                [u'0.00000100', u'49000.00000000']
                            ],
                            u'timestamp': u'1467252600'
                        }
                    },
                },
                {
                    'name':'transactions',
                    'requires':{
                        'book_list': [value for key,value in self.enumerations('order_books').iteritems()]
                    },
                    'optional':{
                        'transaction_time_frame': self.enumerations('transaction_time_frame')[random.choice(self.enumerations('transaction_time_frame').keys())]
                    },
                    'returns':{
                        'btc_cad': [
                            {
                                u'amount': u'0.11052000',
                                u'date': u'1467253487',
                                u'price': u'852.17',
                                u'side': u'sell',
                                u'tid': 249979
                            },
                            {
                                u'amount': u'0.04078998',
                                u'date': u'1467252921',
                                u'price': u'852.17',
                                u'side': u'sell',
                                u'tid': 249978
                            },
                            {
                                u'amount': u'0.01020000',
                                u'date': u'1467251146',
                                u'price': u'852.19',
                                u'side': u'sell',
                                u'tid': 249972
                            }
                        ]
                    },
                },
            ],
            'private':[
                {
                    'name':'balance',
                    'requires': {},
                    'optional': {},
                    'returns':{
                        u'btc_available': u'0.00000000',
                        u'btc_balance': u'0.00500000',
                        u'btc_reserved': u'0.00500000',
                        u'cad_available': u'0.00',
                        u'cad_balance': u'0.00',
                        u'cad_reserved': u'0.00',
                        u'eth_available': u'0.00000000',
                        u'eth_balance': u'0.00000000',
                        u'eth_reserved': u'0.00000000',
                        u'fee': u'0.5000',
                        u'fees': {
                            u'btc_cad': u'0.5000',
                            u'btc_usd': u'0.5000',
                            u'eth_btc': u'0.2000',
                            u'eth_cad': u'0.5000'
                        },
                        u'usd_available': u'0.00',
                        u'usd_balance': u'0.00',
                        u'usd_reserved': u'0.00',
                        u'xau_available': u'0.000000',
                        u'xau_balance': u'0.000000',
                        u'xau_reserved': u'0.000000'
                    },
                },
                {
                    'name':'transactions',
                    'requires':{
                        'book_list': [value for key,value in self.enumerations('order_books').iteritems()]
                    },
                    'optional':{},
                    'returns':{
                        'btc_cad': [
                            {
                                u'amount': u'0.00012000',
                                u'date': u'1467100911',
                                u'price': u'447.94',
                                u'side': u'sell',
                                u'tid': 205503
                            }
                        ]
                    },
                },
                {
                    'name':'open_orders',
                    'requires':{
                        'book_list': [value for key,value in self.enumerations('order_books').iteritems()]
                    },
                    'optional':{},
                    'returns':{
                        'btc_cad': [
                            {
                                u'amount': u'0.00500000',
                                u'datetime': u'2016-06-26 19:15:12',
                                u'id': u'5juqe8mjjxzunll2vtz3wlhwupbwc8fhra86jup3soxfaii6bia83r5yggutpabh',
                                u'price': u'1100.00',
                                u'status': u'0',
                                u'type': u'1'
                            }
                        ]
                    },
                },
                {
                    'name':'lookup_order',
                    'requires':{
                        'order_id': '5juqe8mjjxzunll2vtz3wlhwupbwc8fhra86kup3soxfaii6bia83r5yggutpabh'
                    },
                    'optional':{},
                    'returns':[
                        {
                            u'amount': u'0.00500000',
                            u'book': u'btc_cad',
                            u'created': u'2016-06-26 19:15:12',
                            u'id': u'5juqe8mjjxzunll2vtz3wlhwupbwc8fhra86kup3soxfaii6bia83r5yggutpabh',
                            u'price': u'1100.00',
                            u'status': u'0',
                            u'type': u'1'
                        }
                    ],
                },
                {
                    'name':'cancel_order',
                    'requires':{
                        'order_id': '5juqe8mjjxzunll2vtz3wlhwupbwc8fhra86kup3soxfaii6bia83r5yggutpabh'
                    },
                    'optional':{},
                    'returns':u'true',
                },
                {
                    'name':'buy',
                    'requires':{
                        'book': self.enumerations('order_books')[random.choice(self.enumerations('order_books').keys())],
                        'amount': 0.005,
                    },
                    'optional':{
                        'price': 1000000
                    },
                    'returns':{},
                },
                {
                    'name':'sell',
                    'requires':{
                        'book': self.enumerations('order_books')[random.choice(self.enumerations('order_books').keys())],
                        'amount': 0.010,
                    },
                    'optional':{
                        'price': 1.00
                    },
                    'returns':{},
                },
                {
                    'name':'bitcoin_deposit_address',
                    'requires':{},
                    'optional':{},
                    'returns':u'',
                },
                {
                    'name':'bitcoin_withdrawal',
                    'requires':{
                        'amount': 0.005,
                        'address': ''
                    },
                    'optional':{},
                    'returns':{},
                },
                {
                    'name':'ether_deposit_address',
                    'requires':{},
                    'optional':{},
                    'returns':u'',
                },
                {
                    'name':'ether_withdrawal',
                    'requires':{
                        'amount': 0.005,
                        'address': ''
                    },
                    'optional':{},
                    'returns':{},
                },
            ],
        }

    def public_methods(self):
        return [item['name'] for item in self.methods()['public']]
    def private_methods(self):
        return [item['name'] for item in self.methods()['private']]

    def _enumerator(self, a, options):
        self.logger.debug(a)
        try:
            return options[a]
        except KeyError:
            return { a:[
                '{} is not a valid enumeration'.format(a),
                'the next item in this iterable is an iterable of usable options',
                options.keys()
            ] }

    def _options_preprocessor(self, *options_list):
        """
            This allows the lists in options to be strings, tuples, and lists.
            e.g. Quadriga decides to change their currency codes to uppercase.
            I could change:
            [
                'btc_cad', 'btc_usd', 'eth_btc', 'eth_cad'
            ]
            to:
            [
                ('btc_cad', 'BTC_CAD'), ['btc_usd', 'BTC_USD'],
                ['eth_btc', 'ETH_BTC'], ('eth_cad', 'ETH_CAD')
            ]
            and nobody else would have to change anything.
        """
        options_dict = {}
        for option in options_list:
            self.logger.debug(option)
            if isinstance(option, str) or  isinstance(option, bool):
                options_dict[option] = option
            elif isinstance(option, (list, tuple)):
                if len(option) > 2:
                    self.logger.warning('truncating object from '+option+' to '+option[:2])
                    options_dict[option[0]] = option[1]
                elif len(option) == 2:
                    options_dict[option[0]] = option[1]
                elif len(option) == 1:
                    options_dict[option[0]] = option[0]
                elif len(option) < 1:
                    self.logger.error('contains nothing?')
                    self.logger.error(option)
                else:
                    self.logger.error('mathematically impossible??')
                    self.logger.error(option)
            else:
                self.logger.error('the _options_preprocessor doesn\'t understand this')
                self.logger.error(option)
                return [None, None]
        return options_dict

    def enumerations(self, to_process):

        options = {
            'order_books': self._options_preprocessor( 'btc_cad', 'btc_usd', 'eth_btc', 'eth_cad' ),
            'transaction_time_frame': self._options_preprocessor( 'minute', 'hour' ),
            'group_transactions': self._options_preprocessor( True, False ),
        }

        if isinstance(to_process, list):
            to_return = {}
            for item in to_process:
                to_return[item] = self._enumerator(item, options)
            return to_return
        elif isinstance(to_process, str):
            return self._enumerator(to_process, options)

    def api(self, action, *args, **kwargs):
        ## In the interest of not boring people half to death with the bullshit
        ## details of implementation, some of the arguments passed in need to be
        ## renamed before they can get passed to the interface methods, so if
        ## you want to implement those directly this is a useful list
        arg_names = kwargs.keys()
        name_adjustments = {
            'book_list': 'unchecked_book_list',
            'transaction_time_frame': 'unchecked_time_frame',
            'order_id': 'unchecked_order_id',
            'amount': 'unchecked_amount',
            'price': 'unchecked_price',
        }

        for user_name, api_name in name_adjustments.iteritems():
            if user_name in arg_names:
                kwargs[api_name] = kwargs[user_name]
                del kwargs[user_name]

        # public and private rely on some global functions in this __init__ file,
        # so don't import them until they can get what they need
        if action in self.public_methods():
            from quadriga import public
            return getattr(public, action)(*args, **kwargs)

        elif action in self.private_methods():
            from quadriga import private
            if self.auth:
                return getattr(private, action)(self.auth, *args, **kwargs)

            else:
                return {
                    'status': 'error',
                    'message': 'Authentication required to access this method ({})'.format(action),
                }

        else:
            return {
                'status': 'error',
                'message': '{} not recognized'.format(action),
            }
