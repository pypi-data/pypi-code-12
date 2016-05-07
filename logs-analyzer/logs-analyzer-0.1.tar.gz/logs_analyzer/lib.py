import re
from logs_analyzer.settings import *
from logs_analyzer.validators import *
from datetime import datetime


def get_service_settings(service_name):
    """
    Get default settings for the said service
    :param service_name: service name (example: nginx, apache2...)
    :return: service settings if found or None
    """
    return SERVICES_SWITCHER.get(service_name)


def get_date_filter(settings, minute=datetime.now().minute, hour=datetime.now().hour,
                    day=datetime.now().day, month=datetime.now().month,
                    year=datetime.now().year):
    """
    Get date filter that will be used to filter data from logs based on the params
    :raises Exception:
    :param settings: dict
    :param minute: int
    :param hour: int
    :param day: int
    :param month: int
    :param year: int
    :return: string
    """
    if not is_valid_year(year) or not is_valid_month(month) or not is_valid_day(day) \
            or not is_valid_hour(hour) or not is_valid_minute(minute):
        raise Exception("Date elements aren't valid")
    if minute != '*' and hour != '*':
        date_format = settings['dateminutes_format']
        date_filter = datetime(year, month, day, hour, minute).strftime(date_format)
    elif minute == '*' and hour != '*':
        date_format = settings['datehours_format']
        date_filter = datetime(year, month, day, hour).strftime(date_format)
    elif minute == '*' and hour == '*':
        date_format = settings['datedays_format']
        date_filter = datetime(year, month, day).strftime(date_format)
    else:
        raise Exception("Date elements aren't valid")
    return date_filter


def filter_data(log_filter, data=None, filepath=None, is_casesensitive=True, is_regex=False):
    """
    Filter received data/file content and return the results
    :except IOError:
    :except EnvironmentError:
    :raises Exception:
    :param log_filter: string
    :param data: string
    :param filepath: string
    :param is_casesensitive: boolean
    :param is_regex: boolean
    :return: string
    """
    return_data = ""
    if filepath:
        try:
            with open(filepath, 'r') as file_object:
                for line in file_object:
                    if __check_match(line, log_filter, is_regex, is_casesensitive):
                        return_data += line
            return return_data
        except (IOError, EnvironmentError) as e:
            print(e.strerror)
            exit(2)
    elif data:
        for line in data.splitlines():
            if __check_match(line, log_filter, is_regex, is_casesensitive):
                return_data += line+"\n"
        return return_data
    else:
        raise Exception("Data and filepath values are NULL!")


def __check_match(line, filter_pattern, is_regex, is_casesensitive):
    """
    Check if line contains/matches filter patter
    :param line: string
    :param filter_pattern: string
    :param is_regex: boolean
    :param is_casesensitive: boolean
    :return: boolean
    """
    if is_regex:
        return re.match(filter_pattern, line) if is_casesensitive else re.match(filter_pattern, line, re.IGNORECASE)
    else:
        return (filter_pattern in line) if is_casesensitive else (filter_pattern.lower() in line.lower())


def get_web_requests(data, pattern):
    """
    Analyze data (from the logs) and return list of requests formatted as the model (pattern) defined.
    :param data: string
    :param pattern: string
    :return: list of dicts
    """
    requests_dict = re.findall(pattern, data)
    requests = []
    for request_tuple in requests_dict:
        requests.append({'IP': request_tuple[0], 'DATETIME': request_tuple[1], 'METHOD': request_tuple[2],
                         'ROUTE': request_tuple[3], 'CODE': request_tuple[4], 'REFERRER': request_tuple[5],
                         'USERAGENT': request_tuple[6]})
    return requests


def get_auth_requests(data, pattern):
    """
    Analyze data (from the logs) and return list of auth requests formatted as the model (pattern) defined.
    :param data: string
    :param pattern: string
    :return: list of dicts
    """
    requests_dict = re.findall(pattern, data)
    requests = []
    for request_tuple in requests_dict:
        data = analyze_auth_request(request_tuple[2])
        data['DATETIME'] = request_tuple[0]
        data['SERVICE'] = request_tuple[1]
        requests.append(data)
    return requests


def analyze_auth_request(request_info):
    """
    Analyze request info and returns main data (IP, invalid user, invalid password's user, is_preauth, is_closed)
    :param request_info: string
    :return: dicts
    """
    ipv4 = re.findall(IPv4_REGEX, request_info)
    is_preauth = '[preauth]' in request_info.lower()
    invalid_user = re.findall(AUTH_USER_INVALID_USER, request_info)
    invalid_pass_user = re.findall(AUTH_PASS_INVALID_USER, request_info)
    is_closed = 'connection closed by ' in request_info.lower()
    return {'IP': ipv4[0] if ipv4 else None,
            'INVALID_USER': invalid_user[0] if invalid_user else None,
            'INVALID_PASS_USER': invalid_pass_user[0] if invalid_pass_user else None,
            'IS_PREAUTH': is_preauth,
            'IS_CLOSED': is_closed}
