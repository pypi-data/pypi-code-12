#!/usr/bin/python
from wsgiref.simple_server import make_server

from handlers import general as general_handler

from handlers.util.logger import Logger

from handlers.util import transport as util_transport
import cgi
import re
import mmap
import ast
import ConfigParser

import socket
import uuid
import json
import urllib


# globals
rules = {}
auth_rules = {}
alias_rules = False
actions = {}
port = 0
regex = ''
status_file = False
local_file = False
readable_routes = []
logger = False
auth = False
verbose = False
version = ''
redirect_config = False
temp_folder = ''


def generate_request_id():
    """
    Generates a uuid4 identifier for each request
    :return:
    """
    return str(uuid.uuid4())


def verbose_route(action, action_is_valid, resource_name, route_is_valid):
    """
    Debugging method to verbose results
    """
    print "Last resource is " + resource_name
    print "Routing validation is " + str(route_is_valid)
    print "Action is " + action
    print "Action validation is " + str(action_is_valid)


def calculate_redirect(pathinfo):
    """
    Calculates if the path is pointing towards a redirect scheme
    """
    global redirect_config

    if pathinfo in redirect_config.options('default'):
        destination = redirect_config.get('default', pathinfo)
        return destination
    return False


def calculate_route(rule, pathinfo, method):
    """
    Calculates the ultimate route of the request based on the path info and method
    :param rule:
    :param pathinfo:
    :param method:
    :return: dict
    """
    global readable_routes, alias_rules, version

    try:
        routes = re.findall(rule, pathinfo)
        readable_routes = prepare_full_route(routes=routes)
        last_entity = readable_routes[-1]
        first_entity = readable_routes[0]
        first_entity_name = first_entity['resource']
        resource_name = last_entity['resource']
        resource_id = last_entity['id']

    except IndexError:
        return 'wrong_url'

    alias = calculate_alias(
        resource=first_entity_name,
        method=method,
        requested_action=resource_name,
        requested_id=resource_id
    )

    if alias == 'removed':
        return False

    if alias is not False:
        return {
            'resource': first_entity_name,
            'id': resource_id,
            'action': alias
        }

    route_is_valid = route_resources_are_valid(routes=routes)
    if route_is_valid is False:
        return False

    action = calculate_action(method=method, resource_id=resource_id)

    if action is False:
        return 'invalid_method'

    action_is_valid = resource_allows_action(resource_name=resource_name, action=action)

    if action_is_valid is False:
        return False

    verbose_route(action, action_is_valid, resource_name, route_is_valid)

    return {
        'resource': resource_name,
        'id': resource_id,
        'action': action
    }


def calculate_alias(resource, method, requested_action, requested_id):
    """
    Checks and returns if the url meets an alias from alias.ini
    :param String requested_id: Resource id to be affected
    :param String resource: Resource to affect
    :param String method: HTTP method
    :param String requested_action: Requested action to execute on the resource
    :return:
    """
    global alias_rules
    method = method.lower()

    if alias_rules.has_section(resource) is False:
        return False

    if method + '.' + requested_action in alias_rules.options(resource):
        if alias_rules.get(resource, method + '.' + requested_action) != '':
            return alias_rules.get(resource, method + '.' + requested_action)
        return 'removed'
    if method + '.' + requested_id in alias_rules.options(resource):
        if alias_rules.get(resource, method + '.' + requested_id) != '':
            return alias_rules.get(resource, method + '.' + requested_id)
        return 'removed'
    return False


def prepare_full_route(routes):
    """
    Makes received routes from regex into readable dicts
    :param routes:
    :return:
    """
    route_dict_group = []
    for route in routes:
        path = {
            'resource': route[0],
            'id': route[2]
        }
        route_dict_group.append(path)
    return route_dict_group


def resource_allows_action(resource_name, action):
    """
    Checks if a resource (item, critic, etc) allows a specific action
    :param resource_name:
    :param action:
    :return:
    """
    global rules
    return resource_name in rules and action in rules[resource_name]['actions']


def route_resources_are_valid(routes):
    """
    Checks if the resources requested are valid per conf
    :param routes:
    :return:
    """
    global rules
    for route in routes:
        entity = route[0]
        if entity not in rules:
            return False
    return True


def calculate_action(method, resource_id):
    """
    Calculates the action (list, create, update) from the method and the id
    :param method:
    :param resource_id:
    :return:
    """
    global actions

    for action, fields in actions.items():
        if (method == fields['method'] or method in fields['method']) and (resource_id != '') == fields['id']:
            return action
    return False


def dispatch(environ, start_response):
    """
    Dispatches every request, also checks for possible config changes
    :param environ:
    :param start_response:
    :return:
    """
    global rules, regex, status_file, readable_routes, logger, alias_rules, auth, verbose, version

    if status_file.read(1) != '0':
        reload_all()
    status_file.seek(0)

    method = environ.get('REQUEST_METHOD', '')

    request_id = generate_request_id()

    pathinfo = environ.get('PATH_INFO', '')

    destination = calculate_redirect(
        pathinfo=pathinfo
    )

    if destination is not False:
        query_string = environ.get('QUERY_STRING', '')
        start_response('302 Found', [
            ('Location', str(destination) + '/?' + str(query_string))
        ])
        return []

    transport = {}

    general_rule = re.compile(regex)

    route = calculate_route(
        rule=general_rule,
        pathinfo=pathinfo,
        method=method
    )

    if route == 'wrong_url':
        logger.log_http_response(environ, '404', request_id)
        return general_handler.bad_request(
            environ=environ,
            start_response=start_response,
            transport=transport,
            error=Exception("Endpoint is not available"),
        )
    if route == 'invalid_method':
        logger.log_http_response(environ, '405', request_id)
        return general_handler.bad_method(
            environ=environ,
            start_response=start_response,
            transport=transport
        )
    if route is False:
        logger.log_http_response(environ, '404', request_id)
        return general_handler.url_not_found(
            environ=environ,
            start_response=start_response,
            transport=transport
        )

    resource = route['resource']
    action = route['action']
    query = dict()

    form_data = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=environ,
        keep_blank_values=True
    )

    try:
        if form_data.file is not None:
            body_data = json.loads(form_data.__getattr__('value'))
            for key in body_data:
                query[key] = body_data[key]
    except (TypeError, ValueError):
        pass

    content_type = environ['CONTENT_TYPE']
    try:
        for key in form_data.keys():
            if type(form_data[key]).__name__ != 'list' and form_data[key].filename:
                tmp_name = str(uuid.uuid4())

                write_file(data=form_data.getvalue(key), tmp_name=tmp_name)

                query[key] = dict()
                query[key]['filename'] = form_data[key].filename
                query[key]['file'] = temp_folder + tmp_name
                query[key]['host'] = socket.gethostbyname(socket.gethostname())
            else:
                value = form_data.getvalue(key)
                if content_type == 'application/x-www-form-urlencoded' \
                        or content_type == 'application/x-www-form-urlencoded; charset=utf-8':
                    value = urllib.unquote(value)
                query[key] = value
    except TypeError:
        pass

    logger.log_http_info(environ=environ, message='Serving a request', request_id=request_id, body_params=str(query))

    message = action + ' of ' + resource
    transport = util_transport.prepare_transport(
        message=message,
        query=query,
        paths=readable_routes,
        request_id=request_id,
        verbose=verbose
    )

    try:

        try:
            current_ip = environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            current_ip = environ['REMOTE_ADDR']

        user_agent = environ.get('HTTP_USER_AGENT', '')
        transport['meta']['current_ip'] = current_ip
        transport['meta']['user_agent'] = user_agent

        return general_handler.handle(
            environ=environ,
            start_response=start_response,
            transport=transport,
            resource=resource,
            version=version,
            action=action,
            request_id=request_id,
            logger=logger,
        )
    except (NameError, AttributeError, TypeError, Exception) as e:
        # print str(traceback.format_exc())
        return general_handler.internal_error(
            environ=environ,
            start_response=start_response,
            error=e,
            transport=transport,
            logger=logger,
            request_id=request_id
        )


def start_server():
    """
    Starts listening in desired port
    :return:
    """
    global port
    httpd = make_server('', port, dispatch)
    print "Running Toran on localhost:" + str(port)
    httpd.serve_forever()


def setup():
    """
    Initial setup to load configs and status file
    :return:
    """
    print "setup()..."
    global port, regex, status_file, local_file, logger, alias_rules, auth, verbose, temp_folder
    global redirect_config
    config = ConfigParser.ConfigParser()
    config.read('./config/config.ini')
    port = config.getint('server', 'port')
    regex = ast.literal_eval(config.get('server', 'regex'))
    logger = Logger(config.get('server', 'logger_file'))
    verbose = config.getboolean('server', 'verbose')
    temp_folder = config.get('server', 'temp_folder')

    alias_rules = ConfigParser.ConfigParser()
    alias_rules.read(['./routing/alias.ini', './routing/overlay/alias.ini'])
    alias_rules = alias_rules

    redirect_config = ConfigParser.ConfigParser()
    redirect_config.read('./routing/redirects.ini')

    local_file = open('.status', 'r+')
    local_file.truncate(1)
    status_file = mmap.mmap(local_file.fileno(), 1, mmap.MAP_SHARED, mmap.PROT_WRITE)


def load_actions():
    """
    Loads all the possible actions of the system
    :return:
    """
    print "load_actions()..."
    global actions
    config = ConfigParser.ConfigParser()
    config.read('./routing/actions.ini')
    for action in config.sections():
        action_config = {
            'method': config.get(action, 'method'),
            'id': config.getboolean(action, 'id')
        }
        actions[action] = action_config


def load_rules():
    """
    Loads the rules per resource and what they can do
    :return:
    """
    print "load_rules()..."
    global rules, auth_rules
    config = ConfigParser.ConfigParser()
    config.read(['./routing/rules.ini', './routing/overlay/rules.ini'])
    rules = {}

    for resource in config.sections():
        entity_rules = {
            'actions': config.get(resource, 'actions'),
            # 'parents': config.get(resource, 'parents')
        }
        rules[resource] = entity_rules

    auth_config = ConfigParser.ConfigParser()
    auth_config.read('./routing/auth.ini')
    auth_rules = []

    for auth_level in auth_config.sections():
        for resource in auth_config.options(auth_level):
            action = auth_config.get(auth_level, resource)
            auth_rules.append({resource: {action: auth_level}})


def reload_all():
    """
    Triggers a full reload on the modules and configs, does not restart any requests/threads
    :return:
    """
    global local_file, status_file
    print 'RELOADING!!!'
    reload(general_handler)
    status_file.flush()
    status_file.close()
    local_file.truncate(1)
    status_file = mmap.mmap(local_file.fileno(), 1, mmap.MAP_SHARED, mmap.PROT_WRITE)
    status_file.write('0')
    load_actions()
    load_rules()


def write_file(data, tmp_name):
    with open(temp_folder + tmp_name, 'wb') as f:
        f.write(data)

    return 'tmp_file'


def start(env, start_response):
    return dispatch(env, start_response)


setup()
load_rules()
load_actions()


def run():
    start_server()
