# coding: utf8

import dateutil.parser
from requests import HTTPError
import datetime
import json


def is_string_type(value):
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


def get_json_value(json_data, name):
    if name in json_data:
        return json_data[name]
    else:
        return None


def check_server_error(server_response):
    """
    Check server response.

    Check is the server response contains an HTPP error or a server error.

    :param server_response: request's response
    :type server_response: requests.Response
    :return: nothing

    :raises: Exception('HTTP error : <error_message>) if response contains HTTP response
              ex: '<500 Server error>'
          or Exception('Server error (<error code>) : <server_response>') if UDF returns an error
              ex: {u'ErrorCode': 500, u'ErrorMessage': u'Requested datapoint was not found: News_Headlines', u'Id': u''}

    """
    str_response = str(server_response)

    # check HTTPError on proxy request
    if str_response.startswith('<') and str_response.endswith('>'):
        raise HTTPError(str_response, response=server_response)

    if hasattr(server_response, 'ErrorCode'):
        raise HTTPError(server_response['ErrorMessage'], response=server_response)

    # check UDF error
    if 'ErrorCode' in server_response and 'ErrorMessage' in server_response:
        error_message = server_response['ErrorMessage']
        if len(error_message.split(',')) > 4:
            status, reason_phrase, version, content, headers = error_message.split(',')[:5]
            status_code = status.split(':')[1]
        else:
            status_code = server_response['ErrorCode']
        raise HTTPError(error_message, response=server_response)

    # check DataGrid error
    if 'error' in server_response and 'transactionId' in server_response:
        error_message = server_response['error']
        status_code = 500
        raise HTTPError(error_message, response=server_response)


def to_datetime(date_value):
    if type(date_value) in (datetime.datetime, datetime.date):
        return date_value
    try:
        return dateutil.parser.parse(date_value)
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(e)


def build_listWithParams(values, name):
    if values is None:
        raise ValueError(name + ' is None, it must be a string or a list of strings')

    if is_string_type(values):
        return [(v, None) for v in values.split()]
    elif type(values) is list:
        try:
            return [(value, None) if is_string_type(value) else (value[0], value[1]) for value in values]
        except Exception:
            raise ValueError(name + ' must be a string or a list of strings or a tuple or a list of tuple')
    else:
        try:
            return values[0], values[1]
        except Exception:
            raise ValueError(name + ' must be a string or a list of strings or a tuple or a list of tuple')


def build_list(values, name):
    if values is None:
        raise ValueError(name + ' is None, it must be a string or a list of strings')

    if is_string_type(values):
        return values.split()
    elif type(values) is list:
        if all(is_string_type(value) for value in values):
            return [value for value in values]
        else:
            raise ValueError(name + ' must be a string or a list of strings')
    else:
        raise ValueError(name + ' must be a string or a list of strings')


def build_dictionary(dic, name):
    if dic is None:
        raise ValueError(name + ' is None, it must be a string or a dictionary of strings')

    if is_string_type(dic):
        return json.loads(dic)
    elif type(dic) is dict:
        return dic
    else:
        raise ValueError(name + ' must be a string or aa dictionary')
