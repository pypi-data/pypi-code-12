from django.http import HttpResponse
import json


def get_bool_value(key):
    """
    This method is used to get boolean value from json set value.
    :param key:
    :return:
    """
    bool_val = True
    if not key or key == 'False':
        bool_val = False

    return bool_val


def json_response(response_dict, status=200, cookie=None):
    response = HttpResponse(json.dumps(response_dict), content_type="application/json", status=status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    if cookie:
        response.set_cookie('sessionid_alohomora',cookie)
    return response

