# coding: utf8

import requests
import json
from .tools import is_string_type, check_server_error
from .eikonError import *
import eikon.Profile


def send_json_request(entity, payload, debug=False):
    """
    Returns the JSON response.
    This function can be used for advanced usage or early access to new features.

    Parameters
    ----------
    entity: string
        A string containing a service name

    payload: string
        A string containing a JSON request

    debug: bool, optional
        When set to True, the json request and response are printed.

    Returns
    -------
    string
        The JSON response as a string

    Raises
    ------
    EikonError
        If daemon is disconnected

    requests.Timeout
        If request times out

    Exception
        If request fails (HTTP code other than 200)

    EikonError
        If daemon is disconnected
    """
    profile = eikon.Profile.get_profile()
    if profile:
        if not is_string_type(entity):
            raise ValueError('entity must be a string identifying an UDF endpoint')
        try:
            if is_string_type(payload):
                data = json.loads(payload)
            elif type(payload) is dict:
                data = payload
            else:
                raise ValueError('payload must be a string or a dictionary')
        except json.decoder.JSONDecodeError:
            raise ValueError('payload must be json well formed.')

        try:
            # build the request
            udf_request = {'Entity': {'E': entity, 'W': data}}

            if debug:
                print ('Request: {}'.format(json.dumps(udf_request)))

            response = requests.post(profile.get_url(),
                                     data=json.dumps(udf_request),
                                     headers={'Content-Type': 'application/json',
                                              'x-tr-applicationid': profile.get_application_id()},
                                     timeout=20)

            if debug:
                print('HTTP Response: {} - {}'.format(response.status_code, response.text))

            if response.status_code == 200:
                result = response.json()
                check_server_error(result)
                return result
            if response.status_code == 401:
                raise EikonError('daemon is disconnected')
            else:
                raise requests.HTTPError(str(response), response=response)

        except requests.exceptions.ConnectionError as connectionError:
            if debug:
                print('Connection Error: {}'.format(connectionError))
            raise EikonError('EikonError: {}'.format(connectionError))
        except requests.Timeout as timeout:
            if debug:
                if hasattr(timeout.response, 'status_code'):
                    print('Timeout: {} - {}'.format(timeout.response.status_code, json.dumps(timeout.response.json)))
                else:
                    print('Timeout: {}'.format(timeout))
            raise timeout
        except Exception as e:
            if debug:
                print('Exception: {}'.format(e))
            raise e
