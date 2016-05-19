import os
import re
from datetime import datetime, date

import six
import pandas as pd
from six.moves import configparser
from dateutil import parser

from .sourcedata import (
    is_urlsource,
    recognize_sourcedata,
    dataframe_to_buffer,
)
from .deprecation import deprecated, deprecation_warning

ALL_CAPITAL = re.compile(r'(.)([A-Z][a-z]+)')
CASE_SWITCH = re.compile(r'([a-z0-9])([A-Z])')
UNDERSCORES = re.compile(r'[a-z]_[a-z]{0,1}')

time_fields = frozenset(
    ['time', 'completed_time', 'created_time', 'activated_time',
     'start_time', 'active_time', 'end_time', 'created', 'updated',
     'added_time'])


def underscorize(value):
    partial_result = ALL_CAPITAL.sub(r'\1_\2', value)
    return CASE_SWITCH.sub(r'\1_\2', partial_result).lower()


def underscoreToCamel(match):
    groups = match.group()
    if len(groups) == 2:
        # underscoreToCamel('start_time__gte') -> 'startTime__gte'
        return groups
    return groups[0] + groups[2].upper()


def camelize(value):
    return UNDERSCORES.sub(underscoreToCamel, value)


def get_creds_from_file(config_path):
    cfg_parser = configparser.RawConfigParser()
    cfg_parser.read(config_path)
    username, password, token = None, None, None
    if cfg_parser.has_option('datarobot', 'username'):
        username = cfg_parser.get('datarobot', 'username')
    if cfg_parser.has_option('datarobot', 'password'):
        password = cfg_parser.get('datarobot', 'password')
    if cfg_parser.has_option('datarobot', 'token'):
        token = cfg_parser.get('datarobot', 'token')
    return username, password, token


def get_endpoint_from_file(config_path):
    if config_path:
        cfg_parser = configparser.RawConfigParser()
        cfg_parser.read(config_path)
        try:
            return cfg_parser.get('datarobot', 'endpoint')
        except (configparser.NoSectionError,
                configparser.NoOptionError):
            return None
    return None


def from_api(data, do_recursive=True):
    if type(data) not in (dict, list):
        return data
    if isinstance(data, list):
        return _from_api_list(data, do_recursive=do_recursive)
    return _from_api_dict(data, do_recursive=do_recursive)


def _from_api_dict(data, do_recursive=True):
    app_data = {}
    for k, v in six.iteritems(data):
        if v is None:
            continue
        if k == '_id':
            app_data['id'] = v
            continue
        app_data[underscorize(k)] = from_api(v, do_recursive=do_recursive) if do_recursive else v
    return app_data


def _from_api_list(data, do_recursive=True):
    return [from_api(datum, do_recursive=do_recursive) for datum in data]


def enum(*vals, **enums):
    """
    Enum without third party libs and compatible with py2 and py3 versions.
    """
    enums.update(dict(zip(vals, vals)))
    return type('Enum', (), enums)


def remove_empty_keys(metadata):
    return {k: v for k, v in metadata.items() if v is not None}


def get_endpoint():
    ways_of_endpoint = [
        os.environ.get('DATAROBOT_ENDPOINT'),
        get_endpoint_from_file(get_config_file()),
        'https://app.datarobot.com/api/v2']
    return next(endpoint for endpoint in ways_of_endpoint if endpoint)


def get_config_file():
    if 'DATAROBOT_CONFIG_FILE' in os.environ:
        config_path = os.environ.get('DATAROBOT_CONFIG_FILE')
        if file_exists(config_path):
            return config_path
        else:
            raise ValueError('Bad config path')
    else:
        config_path = os.path.join(os.path.expanduser('~'), '.datarobotrc')
        if file_exists(config_path):
            return config_path
        else:
            return None


file_exists = os.path.isfile


class SetupFieldsMetaclass(type):

    def __new__(cls, name, bases, attrs):
        for field_name in attrs['_fields']:
            attrs.update({field_name: None})
        new_class = super(SetupFieldsMetaclass, cls).__new__(cls,
                                                             name,
                                                             bases,
                                                             attrs)
        return new_class


def parse_time(time_str):
    try:
        return parser.parse(time_str)
    except Exception:
        return time_str


def to_api(data):
    """
    :param data: dictionary {'max_digits': 1}
    :return: {'maxDigits': 1}
    """
    if not data:
        return {}
    assert isinstance(data, dict), 'Wrong type'
    data = remove_empty_keys(data)
    for k, v in six.iteritems(data):
        if isinstance(v, (datetime, date)):
            data[k] = v.isoformat()
    api_data = {camelize(k): to_api(v) if isinstance(v,
                dict) else v for k,
                v in six.iteritems(data)}
    return api_data


def get_id_from_response(response):
    location_string = response.headers['Location']
    return location_string.split('/')[-2]


def get_duplicate_features(features):
    duplicate_features = set()
    seen_features = set()
    for feature in features:
        if feature in seen_features:
            duplicate_features.add(feature)
        else:
            seen_features.add(feature)
    return list(duplicate_features)


def raw_prediction_response_to_dataframe(pred_response):
    """Raw predictions for classification come as nested json objects.

    This will extract it to be a single dataframe.

    Parameters
    ----------
    pred_response : dict
        The loaded json object returned from the prediction route.

    Returns
    -------
    frame : pandas.DataFrame

    """
    predictions = from_api(pred_response)['predictions']
    frame = pd.DataFrame.from_records(predictions)
    return frame
