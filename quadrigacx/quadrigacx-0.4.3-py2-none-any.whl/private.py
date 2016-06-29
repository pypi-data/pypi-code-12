import requests, json, sys
from quadrigacx import check_list_value, check_value
from lobgect import log

logger = log.Log(__name__)







# => @_check_auth
def _check_auth(func):
    def check_auth_inner(auth, *args, **kwargs):
        if not auth:
            logger.error("There's no auth!")
            return {}
        else:
            errors = 0
            for expected_key in ['key', 'client_id', 'secret']:
                if not auth[expected_key]:
                    logger.error("No {} was supplied in the Auth".format(expected_key))
                    errors += 1
            if errors > 0:
                logger.error("{} errors in auth!".format(errors))
                return {}

        logger.debug('Auth is fine.')
        return func(auth, *args, **kwargs)
    return check_auth_inner

@logger.print_post_data
def _post(url, params):
    logger.debug('posting to \'{}\''.format(url))
    post = requests.post( url, data=params )
    try:
        return post.json()
    except ValueError: # Doesn't have a json component
        try:
            return post.text # Honestly this will likely fail if .json() failed, but worth a shot
        except TypeError: # Probably a string response, but pass back whatever.
            return post





@_check_auth
@logger.log_variables
def account_balance(auth):
    logger.info('Getting account balances.')
    url = 'https://api.quadrigacx.com/v2/balance'
    params = auth.auth_params()

    return _post( url, params )


@_check_auth
@logger.log_variables
def user_transactions(auth, unchecked_book_list=None):
    logger.info('Getting account transactions.')
    url = 'https://api.quadrigacx.com/v2/user_transactions'
    books = check_list_value(unchecked_book_list, known_good_options=['btc_cad', 'btc_usd', 'eth_btc', 'eth_cad'])
    response_data = {}

    for book in books:
        params = auth.auth_params()
        params['offset'] = '0'
        params['limit'] = '100'
        params['sort'] = 'desc'
        params['book'] = book
        response_data[book] = _post( url, params )

    return response_data

@_check_auth
@logger.log_variables
def open_orders(auth, unchecked_book_list=None):
    logger.info('Getting open orders.')
    url = 'https://api.quadrigacx.com/v2/open_orders'
    books = check_list_value(unchecked_book_list, known_good_options=['btc_cad', 'btc_usd', 'eth_btc', 'eth_cad'])
    response_data = {}

    for book in books:
        params = auth.auth_params()
        params['book'] = book
        response_data[book] = _post( url, params )
    return response_data






@_check_auth
@logger.log_variables
def lookup_order(auth, unchecked_order_id):
    url = 'https://api.quadrigacx.com/v2/lookup_order'

    params = auth.auth_params()
    params['id'] = check_value(unchecked_order_id, expected_type=None) # Something should be done to check this, but what?

    logger.info('Looking up order: {}'.format(params['id']))

    return _post( url, params )

@_check_auth
@logger.log_variables
def cancel_order(auth, unchecked_order_id):
    url = 'https://api.quadrigacx.com/v2/cancel_order'

    params = auth.auth_params()
    params['id'] = check_value(unchecked_order_id, expected_type=None) # Something should be done to check this, but what?

    logger.info('Cancelling order: {}'.format(params['id']))

    return _post( url, params )

@_check_auth
@logger.log_variables
def buy(auth, unchecked_book, unchecked_amount, unchecked_price=None):
    url = 'https://api.quadrigacx.com/v2/buy'

    params = auth.auth_params()
    params['book'] = check_value(unchecked_book, known_good_options=['btc_cad', 'btc_usd', 'eth_cad', 'btc_eth'])
    params['amount'] = check_value(unchecked_amount, expected_type=float)
    if unchecked_price: # Limit Order // The None case is handled by requests anyway, but I thought it was nice to be explicit
        params['price'] = check_value(unchecked_price, expected_type=float)

    try:
        total = float(params['price']) * float(params['amount'])
    except TypeError:
        total = "ERR"

    if total > 1 and float(params['amount']) >= 0.005 and float(params['price']) >= 10:
        logger.info('Buying {} {} at {} for {} {} total'.format(params['amount'], params['book'][:3].upper(), params['price'], total, params['book'][-3:].upper()))

        return _post( url, params )

    else:
        return {'error':
            {
                'message':'Incorrect value {}{} is below the minimum of $1.00CAD'.format(total, params['book'][-3:].upper())
            }
        }

@_check_auth
@logger.log_variables
def sell(auth, unchecked_book, unchecked_amount, unchecked_price=None):
    url = 'https://api.quadrigacx.com/v2/sell'

    params = auth.auth_params()
    params['book'] = check_value(unchecked_book, known_good_options=['btc_cad', 'btc_usd', 'eth_cad', 'btc_eth'])
    params['amount'] = check_value(unchecked_amount, expected_type=float)
    if unchecked_price: # Limit Order // The None case is handled by requests anyway, but I thought it was nice to be explicit
        params['price'] = check_value(unchecked_price, expected_type=float)

    try:
        total = float(params['price']) * float(params['amount'])
    except TypeError:
        total = "ERR"

    if total > 1 and float(params['amount']) >= 0.005 and float(params['price']) >= 10:
        logger.info('Buying {} {} at {} for {} {} total'.format(params['amount'], params['book'][:3].upper(), params['price'], total, params['book'][-3:].upper()))

        return _post( url, params )

    else:
        return {'error':
            {
                'message':'Incorrect value {}{} is below the minimum of $1.00CAD'.format(total, params['book'][-3:].upper())
            }
        }


@_check_auth
@logger.log_variables
def _deposit_address(auth, currency):
    logger.info( 'Getting {} deposit address.'.format(currency['name']) )
    url = 'https://api.quadrigacx.com/v2/{}'.format(currency['url'])
    params = auth.auth_params()
    return _post( url, params )

def bitcoin_deposit_address(auth):
    currency = {'name': 'Bitcoin', 'url':'bitcoin_deposit_address'}
    return _deposit_address(auth, currency)

def ethereum_deposit_address(auth):
    currency = {'name': 'Ethereum', 'url':'ether_deposit_address'}
    return _deposit_address(auth, currency)


@_check_auth
@logger.log_variables
def _withdraw(auth, url, amount=0, address=None):
    logger.info( 'Withdrawing {} to {}.'.format(amount, address) )
    url = 'https://api.quadrigacx.com/v2/{}'.format( url )
    params = auth.auth_params()
    params['amount'] = check_value(amount, expected_type=float)
    params['address'] = check_value(address, expected_type=str)

    return _post( url, params )

def bitcoin_withdraw(auth, amount, address):
    return _withdraw(auth, url='bitcoin_withdrawal', amount=amount, address=address)

def ethereum_withdraw(auth, amount, address):
    return _withdraw(auth, url='ether_withdrawal', amount=amount, address=address)
