#!/usr/bin/python
#
# (c) 2015, Steve Gargan <steve.gargan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = """
module: consul_acl
short_description: "manipulate consul acl keys and rules"
description:
 - allows the addition, modification and deletion of ACL keys and associated
   rules in a consul cluster via the agent. For more details on using and
   configuring ACLs, see https://www.consul.io/docs/internals/acl.html.
requirements:
  - "python >= 2.6"
  - python-consul
  - pyhcl
  - requests
version_added: "2.0"
author: "Steve Gargan (@sgargan)"
options:
    mgmt_token:
        description:
          - a management token is required to manipulate the acl lists
    state:
        description:
          - whether the ACL pair should be present or absent, defaults to present
        required: false
        choices: ['present', 'absent']
    type:
        description:
          - the type of token that should be created, either management or
            client, defaults to client
        choices: ['client', 'management']
    name:
        description:
          - the name that should be associated with the acl key, this is opaque
            to Consul
        required: false
    token:
        description:
          - the token key indentifying an ACL rule set. If generated by consul
            this will be a UUID.
        required: false
    rules:
        description:
          - an list of the rules that should be associated with a given token.
        required: false
    host:
        description:
          - host of the consul agent defaults to localhost
        required: false
        default: localhost
    port:
        description:
          - the port on which the consul agent is running
        required: false
        default: 8500
"""

EXAMPLES = '''
    - name: create an acl token with rules
      consul_acl:
        mgmt_token: 'some_management_acl'
        host: 'consul1.mycluster.io'
        name: 'Foo access'
        rules:
          - key: 'foo'
            policy: read
          - key: 'private/foo'
            policy: deny

    - name: create an acl with specific token with both key and serivce rules
      consul_acl:
        mgmt_token: 'some_management_acl'
        name: 'Foo access'
        token: 'some_client_token'
        rules:
          - key: 'foo'
            policy: read
          - service: ''
            policy: write
          - service: 'secret-'
            policy: deny

    - name: remove a token
      consul_acl:
        mgmt_token: 'some_management_acl'
        host: 'consul1.mycluster.io'
        token: '172bd5c8-9fe9-11e4-b1b0-3c15c2c9fd5e'
        state: absent
'''

import sys

try:
    import consul
    from requests.exceptions import ConnectionError
    python_consul_installed = True
except ImportError, e:
    python_consul_installed = False

try:
    import hcl
    pyhcl_installed = True
except ImportError:
    pyhcl_installed = False

from requests.exceptions import ConnectionError

def execute(module):

    state = module.params.get('state')

    if state == 'present':
        update_acl(module)
    else:
        remove_acl(module)


def update_acl(module):

    rules = module.params.get('rules')
    state = module.params.get('state')
    token = module.params.get('token')
    token_type = module.params.get('token_type')
    mgmt = module.params.get('mgmt_token')
    name = module.params.get('name')
    consul = get_consul_api(module, mgmt)
    changed = False

    try:

        if token:
            existing_rules = load_rules_for_token(module, consul, token)
            supplied_rules = yml_to_rules(module, rules)
            changed = not existing_rules == supplied_rules
            if changed:
                y = supplied_rules.to_hcl()
                token = consul.acl.update(
                    token,
                    name=name,
                    type=token_type,
                    rules=supplied_rules.to_hcl())
        else:
            try:
                rules = yml_to_rules(module, rules)
                if rules.are_rules():
                    rules = rules.to_hcl()
                else:
                    rules = None

                token = consul.acl.create(
                    name=name, type=token_type, rules=rules)
                changed = True
            except Exception, e:
                module.fail_json(
                    msg="No token returned, check your managment key and that \
                         the host is in the acl datacenter %s" % e)
    except Exception, e:
        module.fail_json(msg="Could not create/update acl %s" % e)

    module.exit_json(changed=changed,
                     token=token,
                     rules=rules,
                     name=name,
                     type=token_type)


def remove_acl(module):
    state = module.params.get('state')
    token = module.params.get('token')
    mgmt = module.params.get('mgmt_token')

    consul = get_consul_api(module, token=mgmt)
    changed = token and consul.acl.info(token)
    if changed:
        token = consul.acl.destroy(token)

    module.exit_json(changed=changed, token=token)

def load_rules_for_token(module, consul_api, token):
    try:
        rules = Rules()
        info = consul_api.acl.info(token)
        if info and info['Rules']:
            rule_set = hcl.loads(to_ascii(info['Rules']))
            for rule_type in rule_set:
                for pattern, policy in rule_set[rule_type].iteritems():
                    rules.add_rule(rule_type, Rule(pattern, policy['policy']))
        return rules
    except Exception, e:
        module.fail_json(
            msg="Could not load rule list from retrieved rule data %s, %s" % (
                    token, e))

    return json_to_rules(module, loaded)

def to_ascii(unicode_string):
    if isinstance(unicode_string, unicode):
        return unicode_string.encode('ascii', 'ignore')
    return unicode_string

def yml_to_rules(module, yml_rules):
    rules = Rules()
    if yml_rules:
        for rule in yml_rules:
            if ('key' in rule and 'policy' in rule):
                rules.add_rule('key', Rule(rule['key'], rule['policy']))
            elif ('service' in rule and 'policy' in rule):
                rules.add_rule('service', Rule(rule['service'], rule['policy']))
            else:
                module.fail_json(msg="a rule requires a key/service and a policy.")
    return rules

template = '''%s "%s" {
  policy = "%s"
}
'''

RULE_TYPES = ['key', 'service']

class Rules:

    def __init__(self):
        self.rules = {}
        for rule_type in RULE_TYPES:
            self.rules[rule_type] = {}

    def add_rule(self, rule_type, rule):
        self.rules[rule_type][rule.pattern] = rule

    def are_rules(self):
        return len(self) > 0

    def to_hcl(self):

        rules = ""
        for rule_type in RULE_TYPES:
            for pattern, rule in self.rules[rule_type].iteritems():
                rules += template % (rule_type, pattern, rule.policy)
        return to_ascii(rules)

    def __len__(self):
        count = 0
        for rule_type in RULE_TYPES:
            count += len(self.rules[rule_type])
        return count

    def __eq__(self, other):
        if not (other or isinstance(other, self.__class__)
                or len(other) == len(self)):
            return False

        for rule_type in RULE_TYPES:
            for name, other_rule in other.rules[rule_type].iteritems():
                if not name in self.rules[rule_type]:
                    return False
                rule = self.rules[rule_type][name]

                if not (rule and rule == other_rule):
                    return False
        return True

    def __str__(self):
        return self.to_hcl()

class Rule:

    def __init__(self, pattern, policy):
        self.pattern = pattern
        self.policy = policy

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.pattern == other.pattern
                and self.policy == other.policy)

    def __hash__(self):
        return hash(self.pattern) ^ hash(self.policy)

    def __str__(self):
        return '%s %s' % (self.pattern, self.policy)

def get_consul_api(module, token=None):
    if not token:
        token = module.params.get('token')
    return consul.Consul(host=module.params.get('host'),
                         port=module.params.get('port'),
                         token=token)

def test_dependencies(module):
    if not python_consul_installed:
        module.fail_json(msg="python-consul required for this module. "\
              "see http://python-consul.readthedocs.org/en/latest/#installation")

    if not pyhcl_installed:
        module.fail_json( msg="pyhcl required for this module."\
              " see https://pypi.python.org/pypi/pyhcl")

def main():
    argument_spec = dict(
        mgmt_token=dict(required=True, no_log=True),
        host=dict(default='localhost'),
        name=dict(required=False),
        port=dict(default=8500, type='int'),
        rules=dict(default=None, required=False, type='list'),
        state=dict(default='present', choices=['present', 'absent']),
        token=dict(required=False, no_log=True),
        token_type=dict(
            required=False, choices=['client', 'management'], default='client')
    )
    module = AnsibleModule(argument_spec, supports_check_mode=False)

    test_dependencies(module)

    try:
        execute(module)
    except ConnectionError, e:
        module.fail_json(msg='Could not connect to consul agent at %s:%s, error was %s' % (
                            module.params.get('host'), module.params.get('port'), str(e)))
    except Exception, e:
        module.fail_json(msg=str(e))

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
