# coding: utf8

import pandas as pd
import eikon.json_requests
from .tools import is_string_type, build_list

Symbology_UDF_endpoint = 'SymbologySearch'
KeyNames = ['cusips', 'isins', 'rics', 'sedols', 'best_match', 'primary_rics', 'symbol', 'error', 'json_raw']
Symbol_Types = ['CUSIP', 'ISIN', 'SEDOL', 'RIC', 'ticker']


def get_symbology(symbol, from_symbol_type='RIC', to_symbol_type=None, output='pandas', debug=False):
    """
    Returns a list of instrument names converted into another instrument code.
    For example: convert SEDOL instrument names to RIC names

    Parameters
    ----------
    symbol: string or list of strings
        Single instrument or list of instruments to convert.
    from_symbol_type: string
        Instrument code to convert from.
        Possible values: 'CUSIP', 'ISIN', 'SEDOL', 'RIC', 'ticker' (Default 'RIC')
    to_symbol_type: string or list
        Instrument code to convert to.
        Possible values: 'CUSIP', 'ISIN', 'SEDOL', 'RIC', 'ticker'
    output: string
        By default the output is a pandas.DataFrame.
        Set output='raw' to get data in Json format.
    debug: bool
        When set to True, the json request and response are printed.

    Returns
    -------
    pandas.DataFrame
        The pandas.DataFrame columns are:

        - columns             : Symbol types
        - rows                : Symbol requested
        - cells               : the symbols (None if not found)
        - symbol              : The requested symbol

    Raises
    ------
    Exception
        If request fails or if server returns an error
    ValueError
        If a parameter type or value is wrong

    Examples
    --------
    >>> import eikon as ek
    >>> ek.set_app_id('set your app id here')
    >>> ISIN_codes = ek.get_symbology(["MSFT.O", "GOOG.O", "IBM.N"], from_symbol_type="RIC", to_symbol_type="ISIN")
    >>> ISIN_codes
                    ISIN
    MSFT.O  US5949181045
    GOOG.O  US02079K1079
    IBM.N   US4592001014
    """

    # set the symbol(s) in the payload
    payload = {"symbols": build_list(symbol, 'symbol')}

    # set the from in the payload
    if is_string_type(from_symbol_type):
        payload.update({'from': from_symbol_type})
    else:
        raise ValueError('from_symbol_type must be a string')

    # set the to(s) in the payload
    if to_symbol_type is not None:
        if is_string_type(to_symbol_type):
            to_symbol_type = [to_symbol_type]

        if type(to_symbol_type) is list and all(is_string_type(symbol) is True for symbol in to_symbol_type):
            payload.update({'to': to_symbol_type})
        else:
            raise ValueError('to_symbol_type must be a string or a list of strings')

    payload.update({'bestMatchOnly': True})

    result = eikon.json_requests.send_json_request(Symbology_UDF_endpoint, payload, debug=debug)

    if output.lower() == 'raw':
        return result

    seen = set()
    symbol_type = [st for st in [key for keys in [list(mappedSymbol['bestMatch'].keys()) for mappedSymbol in
                                                  result['mappedSymbols']] for key in keys] if
                                                                st not in seen and not seen.add(st)]
    if 'primaryRIC' in symbol_type:
        symbol_type.remove('primaryRIC')

    numpy_array = [[vals.get(val) for val in symbol_type] for vals in
                   [mappedSymbol['bestMatch'] for mappedSymbol in result['mappedSymbols']]]
    reqSymbol = [mappedSymbol['symbol'] for mappedSymbol in result['mappedSymbols']]
    return pd.DataFrame(numpy_array, columns=symbol_type, index=reqSymbol)
