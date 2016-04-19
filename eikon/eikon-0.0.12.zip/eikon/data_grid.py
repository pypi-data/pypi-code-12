# coding: utf8

import pandas as pd
import numpy as np

import eikon.json_requests
from .tools import is_string_type, build_list, get_json_value, build_dictionary, build_listWithParams

DataGrid_UDF_endpoint = 'DataGrid'


def get_data(instruments, fields, parameters=None, sort_on=None, output='pandas', debug=False):
    """
    Returns a pandas.DataFrame with fields in columns and instruments as row index

    Parameters
    ----------
    instruments: string or list
        Single instrument or list of instruments to request.

    fields: string or list
        Single field or list of fields to request.
        Fields can be either a string containing the field name or
        A tuple made of the field name and a dictionary of parameters.

        Example to convert the gross profit in Euro and format in million:
           ('TR.GrossProfit' ,{ 'Scale': 6, 'Curn': 'EUR' })

        Tips: You can launch the Data Item Browser to discover fields and parameters
        or copy field names and parameters from TR Eikon - MS Office formulas

    parameters: string or dictionary
        Single global parameter key=value or dictionary of global parameters to request.

    sort_on: string or dict or list of string and/or dict (optional)
        Single field or list of fields to sort result on
        Default: None
            Examples:
                'TR.PriceClose'

                {'TR.PriceClose':'desc'}

                ['TR.PriceClose', {'TR.PriceOpen': 'desc'}]

    output: string
        By default the output is a pandas.DataFrame.
        Set output='raw' to get data in Json format.

    debug: bool
        When set to True, the json request and response are printed.

    Returns
    -------
    pandas.DataFrame
        Returns pandas.DataFrame with fields in columns and instruments as row index

    errors
        Returns a list of errors

    Raises
    ----------
    Exception
        If http request fails or if server returns an error
    ValueError
        If a parameter type or value is wrong

    Examples
    --------
    >>> import eikon as ek
    >>> ek.set_app_id('set your app id here')
    >>> data_grid, err = ek.get_data(["IBM", "GOOG.O", "MSFT.O"], ["TR.PriceClose", "TR.Volume", "TR.PriceLow"])
    >>> data_grid, err = ek.get_data("IBM", ['TR.Employees', ('TR.GrossProfit', {'Scale': 6, 'Curn': 'EUR'})])
    """

    # check instruments parameter
    instrument_list = build_list(instruments, 'instruments')

    # check fields parameter
    field_list = build_listWithParams(fields, 'fields')

    if parameters:
        parameter_dic = build_dictionary(parameters, 'parameters')
    else:
        parameter_dic = None

    sort_on_fields = []
    sort_orders = {}
    sort_priority = {}
    index = 0
    # check the sort_on parameter
    if sort_on is not None:
        if is_string_type(sort_on) or type(sort_on) is dict:
            sort_on = [sort_on]
        for sort_criteria in sort_on:
            if type(sort_criteria) is dict:
                for field, sort_order in sort_criteria.iteritems():
                    if sort_order not in ['asc', 'desc']:
                        raise AttributeError("sort order must be in ['asc','desc']")
                    if field in [f[0] for f in field_list]:
                        sort_on_fields.append(field)
                        sort_orders[field] = sort_order
                        sort_priority[field] = index
                        index += 1
            elif is_string_type(sort_criteria) and sort_criteria in [f[0] for f in field_list]:
                sort_on_fields.append(sort_criteria)
                sort_orders[sort_criteria] = 'asc'
                sort_priority[sort_criteria] = index
                index += 1
            else:
                raise AttributeError('sort_on must be a string or a list of strings')

    payload = {'instruments': instrument_list}

    selected_fields = []
    for field in field_list:
        json_field = {'name': field[0]}
        if field[0] in sort_on_fields:
            json_field.update({'sort': sort_orders[field[0]]})
            json_field.update({'sortPriority': sort_priority[field[0]]})
        if field[1] is not None:
            json_field.update({'parameters': field[1]})
        selected_fields.append(json_field)

    payload.update({'fields': selected_fields})
    if parameter_dic:
        payload.update({'parameters': parameter_dic})
    result = eikon.json_requests.send_json_request(DataGrid_UDF_endpoint, payload, debug=debug)
    if output.lower == 'raw':
        return result['data'], None

    pandas_result, errors = convert_json_to_pandas(result)
    return pandas_result, errors


def convert_json_to_pandas(json_result):
    _headers = [header['displayName'] for header in json_result['headers'][0]]
    _numpy_array = np.array([[get_data_value(value) for value in row] for row in json_result['data']])
    dataframe = pd.DataFrame(_numpy_array, columns=_headers)
    dataframe = dataframe.apply(pd.to_numeric, errors='ignore')
    errors = get_json_value(json_result, 'error')
    return dataframe, errors


def get_data_value(value):
    if is_string_type(value):
        return value
    elif value is dict:
        return value['value']
    else:
        return value
