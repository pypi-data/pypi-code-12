#!/usr/bin/python
import ConfigParser
import argparse
import subprocess


def run():
    parser = argparse.ArgumentParser(description='CLI Tool to change configs')

    parser.add_argument(
        '--action',
        choices=['REMOVE', 'RESET'],
        required=True,
        help='Action to excerpt on the given resource.endpoint'
    )

    parser.add_argument(
        '--resource',
        required=True,
        help='Resource that will be changed (users, sessions, etc)'
    )

    parser.add_argument(
        '--endpoint',
        help='Endpoint that belongs to the specified resource that will change'
    )

    args = parser.parse_args()

    resource = args.resource
    action = args.action
    endpoint = args.endpoint

    confirmation = True
    if endpoint is None:
        confirmation = confirm(prompt='Are you sure you want to change a complete resource?')

    if confirmation is False:
        print 'Canceling config change'

    handle_config_changes(resource=resource, action=action, endpoint=endpoint)
    print 'process completed'
    subprocess.call(['sudo', 'supervisorctl', 'restart', 'gateway'])


def confirm(prompt=None, resp=False):
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def handle_config_changes(action, resource, endpoint):
    if action == 'REMOVE':
        handle_remove_endpoint(resource, endpoint)
    elif action == 'RESET':
        handle_reset_endpoint(resource, endpoint)
    pass


def handle_remove_endpoint(resource, endpoint):
    if endpoint is None:
        remove_resource(resource)
    else:
        remove_endpoint(resource, endpoint)


def remove_resource(resource):
    overlay_rules_config = ConfigParser.ConfigParser()
    overlay_rules_config.read('./routing.default/overlay/rules.ini')

    if resource not in overlay_rules_config.sections():
        overlay_rules_config.add_section(resource)

    overlay_rules_config.set(resource, 'actions', '')
    with open(r'./routing.default/overlay/rules.ini', 'wb') as configfile:
        overlay_rules_config.write(configfile)

    alias_config = ConfigParser.ConfigParser()
    alias_config.read('./routing.default/alias.ini')

    overlay_alias_config = ConfigParser.ConfigParser()
    overlay_alias_config.read('./routing.default/overlay/alias.ini')

    if resource not in overlay_alias_config.sections():
        overlay_alias_config.add_section(resource)

    for option in alias_config.options(resource):
        overlay_alias_config.set(resource, option, '')

    with open(r'./routing.default/overlay/alias.ini', 'wb') as configfile:
        overlay_alias_config.write(configfile)


def remove_endpoint(resource, endpoint):
    actions_config = ConfigParser.ConfigParser()
    actions_config.read('./routing.default/actions.ini')

    if endpoint in actions_config.sections():
        remove_endpoint_rules(resource, endpoint)
    else:
        remove_endpoint_alias(resource, endpoint)

    pass


def remove_endpoint_rules(resource, endpoint):
    rules_config = ConfigParser.ConfigParser()
    rules_config.read('./routing.default/rules.ini')

    rules_options = rules_config.get(resource, 'actions')

    overlay_rules_config = ConfigParser.ConfigParser()
    overlay_rules_config.read('./routing.default/overlay/rules.ini')

    if resource not in overlay_rules_config.sections():
        overlay_rules_config.add_section(resource)
        overlay_rules_config.set(resource, 'actions', '')

    overlay_rules_options = overlay_rules_config.get(resource, 'actions')

    rules_intersection = rules_options.split(',')

    if len(filter(bool, overlay_rules_options.split(','))) > 0:
        rules_intersection = set(rules_intersection).intersection(overlay_rules_options.split(','))

    rules_intersection.remove(endpoint)

    result = ','.join(rules_intersection)

    overlay_rules_config.set(resource, 'actions', result)
    with open(r'./routing.default/overlay/rules.ini', 'wb') as configfile:
        overlay_rules_config.write(configfile)


def remove_endpoint_alias(resource, endpoint):
    alias_config = ConfigParser.ConfigParser()
    alias_config.read('./routing.default/alias.ini')

    existing_alias = False
    for option in alias_config.options(resource):
        if endpoint == alias_config.get(resource, option):
            existing_alias = option

    if existing_alias is False:
        print 'endpoint not found in previous config'
        return False

    overlay_alias_config = ConfigParser.ConfigParser()
    overlay_alias_config.read('./routing.default/overlay/alias.ini')

    if resource not in overlay_alias_config.sections():
        overlay_alias_config.add_section(resource)
        overlay_alias_config.set(resource, existing_alias, '')
    else:
        overlay_alias_config.set(resource, existing_alias, '')

    with open(r'./routing.default/overlay/alias.ini', 'wb') as configfile:
        overlay_alias_config.write(configfile)


def handle_reset_endpoint(resource, endpoint):
    if endpoint is None:
        reset_resource(resource)
    else:
        reset_endpoint(resource, endpoint)


def reset_resource(resource):
    overlay_rules_config = ConfigParser.ConfigParser()
    overlay_rules_config.read('./routing.default/overlay/rules.ini')

    if resource not in overlay_rules_config.sections():
        overlay_rules_config.add_section(resource)

    overlay_rules_config.remove_section(resource)

    with open(r'./routing.default/overlay/rules.ini', 'wb') as configfile:
        overlay_rules_config.write(configfile)

    overlay_alias_config = ConfigParser.ConfigParser()
    overlay_alias_config.read('./routing.default/overlay/alias.ini')

    if resource not in overlay_alias_config.sections():
        overlay_alias_config.add_section(resource)

    overlay_alias_config.remove_section(resource)

    with open(r'./routing.default/overlay/alias.ini', 'wb') as configfile:
        overlay_alias_config.write(configfile)


def reset_endpoint(resource, endpoint):
    actions_config = ConfigParser.ConfigParser()
    actions_config.read('./routing.default/actions.ini')

    if endpoint in actions_config.sections():
        reset_endpoint_rules(resource, endpoint)
    else:
        reset_endpoint_alias(resource, endpoint)


def reset_endpoint_rules(resource, endpoint):
    rules_config = ConfigParser.ConfigParser()
    rules_config.read('./routing.default/rules.ini')

    rules_options = rules_config.get(resource, 'actions')

    overlay_rules_config = ConfigParser.ConfigParser()
    overlay_rules_config.read('./routing.default/overlay/rules.ini')

    if resource not in overlay_rules_config.sections():
        overlay_rules_config.add_section(resource)
        overlay_rules_config.set(resource, 'actions', '')

    overlay_rules_options = overlay_rules_config.get(resource, 'actions')

    rules_intersection = rules_options.split(',')

    if len(filter(bool, overlay_rules_options.split(','))) > 0:
        rules_intersection = set(rules_intersection).intersection(overlay_rules_options.split(','))

    rules_intersection.add(endpoint)

    result = ','.join(rules_intersection)

    overlay_rules_config.set(resource, 'actions', result)
    with open(r'./routing.default/overlay/rules.ini', 'wb') as configfile:
        overlay_rules_config.write(configfile)


def reset_endpoint_alias(resource, endpoint):
    alias_config = ConfigParser.ConfigParser()
    alias_config.read('./routing.default/alias.ini')

    existing_alias = False
    for option in alias_config.options(resource):
        if endpoint == alias_config.get(resource, option):
            existing_alias = option

    if existing_alias is False:
        print 'endpoint not found in previous config'
        return False

    overlay_alias_config = ConfigParser.ConfigParser()
    overlay_alias_config.read('./routing.default/overlay/alias.ini')

    if resource not in overlay_alias_config.sections():
        overlay_alias_config.add_section(resource)

    if existing_alias in overlay_alias_config.options(resource):
        overlay_alias_config.remove_option(resource, existing_alias)
        with open(r'./routing.default/overlay/alias.ini', 'wb') as configfile:
            overlay_alias_config.write(configfile)

# ---------------------------- #
# main configChanger call      #
# ---------------------------- #
if __name__ == '__main__':
    run()
