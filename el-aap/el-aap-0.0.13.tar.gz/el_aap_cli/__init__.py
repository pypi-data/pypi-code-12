__author__ = 'schlitzer'
# stdlib
import argparse
import configparser
import json
import os
import requests
import sys


def main():
    parser = argparse.ArgumentParser(description="ElasticSearch Authentication and Authorization command line utility")

    subparsers = parser.add_subparsers(help='commands', dest='method')
    subparsers.required = True

    permissions_parser = subparsers.add_parser('permissions', help='manage permissions')
    permissions_parser.set_defaults(method='permissions')

    permissions_subparsers = permissions_parser.add_subparsers(help='commands', dest='submethod')
    permissions_subparsers.required = True

    permissions_add_parser = permissions_subparsers.add_parser('add', help='add permission rule')
    permissions_add_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_add_parser.add_argument('--description', dest='description', action='store', required=True)
    permissions_add_parser.add_argument('--scope', dest='scope', action='store', required=True)
    permissions_add_parser.add_argument(
        '--permissions', dest='permissions', action='store', required=True,
        help='comma seperated list of enabled permissions for this rule'
    )
    permissions_add_parser.add_argument(
        '--roles', dest='roles', action='store', required=True,
        help='comma seperated list of enabled permissions for this rule'
    )
    permissions_del_parser = permissions_subparsers.add_parser('del', help='delete permission rule')
    permissions_del_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_get_parser = permissions_subparsers.add_parser('get', help='get permission rule')
    permissions_get_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_update_parser = permissions_subparsers.add_parser('update', help='update permission rule')
    permissions_update_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_update_parser.add_argument('--description', dest='description', action='store', default=None)
    permissions_update_parser.add_argument('--scope', dest='scope', action='store', default=None)
    permissions_update_parser.add_argument(
        '--permissions', dest='permissions', action='store', default=None,
        help='comma seperated list of enabled permissions for this rule'
    )
    permissions_update_parser.add_argument(
        '--roles', dest='roles', action='store', default=None,
        help='comma seperated list of roles belonging to this rule'
    )
    permissions_search_parser = permissions_subparsers.add_parser('search', help='search permission rules')
    permissions_search_parser.add_argument('--id', dest='id', action='store', default=None)
    permissions_search_parser.add_argument(
        '--permissions', dest='permissions', action='store', default=None,
        help='comma seperated list of permissions'
    )
    permissions_search_parser.add_argument(
        '--roles', dest='roles', action='store', default=None,
        help='comma seperated list of roles'
    )
    permissions_search_parser.add_argument(
        '--scopes', dest='scopes', action='store', default=None,
        help='comma seperated list of scopes'
    )
    permissions_add_permissions_parser = permissions_subparsers.add_parser(
        'add_permissions', help='add permission from existing rule')
    permissions_add_permissions_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_add_permissions_parser.add_argument(
        '--permissions', dest='permissions', action='store', required=True,
        help='comma seperated list of permissions'
    )
    permissions_del_permissions_parser = permissions_subparsers.add_parser(
        'del_permissions', help='delete permission from existing rule')
    permissions_del_permissions_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_del_permissions_parser.add_argument(
        '--permissions', dest='permissions', action='store', required=True,
        help='comma seperated list of permissions'
    )
    permissions_add_roles_parser = permissions_subparsers.add_parser(
        'add_roles', help='add roles to existing rule')
    permissions_add_roles_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_add_roles_parser.add_argument(
        '--roles', dest='roles', action='store', required=True,
        help='comma seperated list of roles'
    )
    permissions_del_roles_parser = permissions_subparsers.add_parser(
        'del_roles', help='delete roles from existing rule')
    permissions_del_roles_parser.add_argument('--id', dest='id', action='store', required=True)
    permissions_del_roles_parser.add_argument(
        '--roles', dest='roles', action='store', required=True,
        help='comma seperated list of roles'
    )

    roles_parser = subparsers.add_parser('roles', help='manage roles')
    roles_parser.set_defaults(method='roles')

    roles_subparsers = roles_parser.add_subparsers(help='commands', dest='submethod')
    roles_subparsers.required = True

    roles_add_parser = roles_subparsers.add_parser('add', help='add role definition')
    roles_add_parser.add_argument('--id', dest='id', action='store', required=True)
    roles_add_parser.add_argument('--description', dest='description', action='store', required=True)
    roles_add_parser.add_argument(
        '--users', dest='users', action='store', required=True,
        help='comma seperated list of users ids that belong to this role'
    )
    roles_del_parser = roles_subparsers.add_parser('del', help='delete role definition')
    roles_del_parser.add_argument('--id', dest='id', action='store', required=True)
    roles_get_parser = roles_subparsers.add_parser('get', help='get role definition')
    roles_get_parser.add_argument('--id', dest='id', action='store', required=True)
    roles_update_parser = roles_subparsers.add_parser('update', help='update role definition')
    roles_update_parser.add_argument('--id', dest='id', action='store', required=True)
    roles_update_parser.add_argument('--description', dest='description', action='store', default=None)
    roles_update_parser.add_argument(
        '--users', dest='users', action='store', default=None,
        help='comma seperated list of users ids that belong to this role'
    )
    roles_search_parser = roles_subparsers.add_parser('search', help='find roles')
    roles_search_parser.add_argument('--id', dest='id', action='store', default=None)
    roles_search_parser.add_argument(
        '--users', dest='users', action='store', default=None,
        help='comma seperated list of users ids that belong to this role'
    )
    roles_add_users_parser = roles_subparsers.add_parser('add_users', help='add users to role')
    roles_add_users_parser.add_argument('--id', dest='id', action='store', required=True)
    roles_add_users_parser.add_argument(
        '--users', dest='users', action='store', required=True,
        help='comma seperated list of users to add to this role'
    )
    roles_del_users_parser = roles_subparsers.add_parser('del_users', help='delete users from role')
    roles_del_users_parser.add_argument('--id', dest='id', action='store', required=True)
    roles_del_users_parser.add_argument(
        '--users', dest='users', action='store', required=True,
        help='comma seperated list of users to remove from this role'
    )

    users_parser = subparsers.add_parser('users', help='manage users')
    users_parser.set_defaults(method='users')

    users_subparsers = users_parser.add_subparsers(help='commands', dest='submethod')
    users_subparsers.required = True

    users_add_parser = users_subparsers.add_parser('add', help='add user')
    users_add_parser.add_argument('--id', dest='id', action='store', required=True)
    users_add_parser.add_argument('--admin', dest='admin', action='store_true', required=False, default=False)
    users_add_parser.add_argument('--email', dest='email', action='store', required=True)
    users_add_parser.add_argument('--name', dest='name', action='store', required=True)
    users_add_parser.add_argument('--password', dest='password', action='store', required=True)
    users_del_parser = users_subparsers.add_parser('del', help='delete user')
    users_del_parser.add_argument('--id', dest='id', action='store', required=True)
    users_get_parser = users_subparsers.add_parser('get', help='get user')
    users_get_parser.add_argument('--id', dest='id', action='store', required=True)
    users_update_parser = users_subparsers.add_parser('update', help='update user')
    users_update_parser.add_argument('--id', dest='id', action='store', required=True)
    users_update_parser.add_argument('--admin', dest='admin', action='store_true', default=None)
    users_update_parser.add_argument('--email', dest='email', action='store', default=None)
    users_update_parser.add_argument('--name', dest='name', action='store', default=None)
    users_update_parser.add_argument('--password', dest='password', action='store', default=None)
    users_search_parser = users_subparsers.add_parser('search', help='find users')
    users_search_parser.add_argument('--id', dest='id', action='store', default=None)

    parsed_args = parser.parse_args()

    el_aapcli = ElasticSearchAAPCLI()
    if parsed_args.method == 'permissions':
        if parsed_args.submethod == 'add':
            el_aapcli.perm_add(
                _id=parsed_args.id,
                description=parsed_args.description,
                scope=parsed_args.scope,
                permissions=parsed_args.permissions,
                roles=parsed_args.roles
            )
        elif parsed_args.submethod == 'del':
            el_aapcli.perm_del(
                _id=parsed_args.id,
            )
        elif parsed_args.submethod == 'get':
            el_aapcli.perm_get(
                _id=parsed_args.id,
            )
        elif parsed_args.submethod == 'update':
            el_aapcli.perm_update(
                _id=parsed_args.id,
                description=parsed_args.description,
                scope=parsed_args.scope,
                permissions=parsed_args.permissions,
                roles=parsed_args.roles
            )
        elif parsed_args.submethod == 'search':
            el_aapcli.perm_search(
                _id=parsed_args.id,
                scopes=parsed_args.scopes,
                permissions=parsed_args.permissions,
                roles=parsed_args.roles
            )
        elif parsed_args.submethod == 'add_permissions':
            el_aapcli.perm_add_perms(
                _id=parsed_args.id,
                permissions=parsed_args.permissions,
            )
        elif parsed_args.submethod == 'del_permissions':
            el_aapcli.perm_del_perms(
                _id=parsed_args.id,
                permissions=parsed_args.permissions,
            )
        elif parsed_args.submethod == 'add_roles':
            el_aapcli.perm_add_roles(
                _id=parsed_args.id,
                roles=parsed_args.roles
            )
        elif parsed_args.submethod == 'del_roles':
            el_aapcli.perm_del_roles(
                _id=parsed_args.id,
                roles=parsed_args.roles
            )

    elif parsed_args.method == 'roles':
        if parsed_args.submethod == 'add':
            el_aapcli.roles_add(
                _id=parsed_args.id,
                description=parsed_args.description,
                users=parsed_args.users,
            )
        elif parsed_args.submethod == 'del':
            el_aapcli.roles_del(
                _id=parsed_args.id,
            )
        elif parsed_args.submethod == 'get':
            el_aapcli.roles_get(
                _id=parsed_args.id,
            )
        elif parsed_args.submethod == 'update':
            el_aapcli.roles_update(
                _id=parsed_args.id,
                description=parsed_args.description,
                users=parsed_args.users,
            )
        elif parsed_args.submethod == 'search':
            el_aapcli.roles_search(
                _id=parsed_args.id,
                users=parsed_args.users,
            )
        elif parsed_args.submethod == 'add_users':
            el_aapcli.roles_add_users(
                _id=parsed_args.id,
                users=parsed_args.users,
            )
        elif parsed_args.submethod == 'del_users':
            el_aapcli.roles_del_users(
                _id=parsed_args.id,
                users=parsed_args.users,
            )

    elif parsed_args.method == 'users':
        if parsed_args.submethod == 'add':
            el_aapcli.users_add(
                _id=parsed_args.id,
                admin=parsed_args.admin,
                email=parsed_args.email,
                name=parsed_args.name,
                password=parsed_args.password
            )
        elif parsed_args.submethod == 'del':
            el_aapcli.users_del(
                _id=parsed_args.id,
            )
        elif parsed_args.submethod == 'get':
            el_aapcli.users_get(
                _id=parsed_args.id,
            )
        elif parsed_args.submethod == 'update':
            el_aapcli.users_update(
                _id=parsed_args.id,
                admin=parsed_args.admin,
                email=parsed_args.email,
                name=parsed_args.name,
                password=parsed_args.password
            )
        elif parsed_args.submethod == 'search':
            el_aapcli.users_search(
                _id=parsed_args.id,
            )


class ElasticSearchAAPCLI(object):
    def __init__(self):
        self._config = configparser.ConfigParser()
        try:
            self._config.read_file(open(os.path.expanduser('~/.el_aap_cli.ini')))
        except FileNotFoundError:
            print('Could not read configfile, please create: ~/.el_aap_cli.ini')
            sys.exit(1)
        try:
            self.endpoint = self._config.get('main', 'endpoint')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the endpoint in the main section')
            sys.exit(1)
        try:
            self.user = self._config.get('main', 'user')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the user in the main section')
            sys.exit(1)
        try:
            self.password = self._config.get('main', 'pass')
        except (configparser.NoOptionError, configparser.NoSectionError):
            print('please configure the password in the main section')
            sys.exit(1)
        self.session = self._test_session()
        if not self.session:
            self.session = self._get_session()

    def _get_session(self):
        login = {'user': self.user, 'password': self.password}
        request = requests.post(self.endpoint+'elaap/api/v1/authenticate', json=login)
        if not request.status_code == 201:
            print('invalid login credentials specified')
            sys.exit(1)
        session = {
            'X-SID': request.json()['_id'],
            'X_TOKEN': request.json()['token']
        }
        with open(os.path.expanduser('~/.el_aap_cli.session'), 'w') as outfile:
            json.dump(session, outfile)
        return session

    def _test_session(self):
        try:
            with open(os.path.expanduser('~/.el_aap_cli.session')) as infile:
                session = json.load(infile)
        except (ValueError, FileNotFoundError):
            return

        request = requests.get(self.endpoint+'elaap/api/v1/users/_self', headers=session)
        if request.status_code == 200:
            return session

    def perm_add(self, _id, description, scope, permissions, roles):
        payload = {
            '_id': _id,
            'description': description,
            'scope': scope,
            'permissions': permissions.split(','),
            'roles': roles.split(',')
        }
        url = self.endpoint+'elaap/api/v1/permissions'
        request = requests.post(url, json=payload, headers=self.session)
        if request.status_code == 201:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def perm_del(self, _id):
        url = self.endpoint+'elaap/api/v1/permissions/'+_id
        request = requests.delete(url, headers=self.session)
        if request.status_code == 200:
            print('permission deleted')
        else:
            print(request.json())
            sys.exit(1)

    def perm_get(self, _id):
        url = self.endpoint+'elaap/api/v1/permissions/'+_id
        request = requests.get(url, headers=self.session)
        if request.status_code == 202:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def perm_update(self, _id, description, scope, permissions, roles):
        payload = {}
        if description is not None:
            payload['description'] = description
        if scope is not None:
            payload['scope'] = scope
        if permissions is not None:
            payload['permissions'] = permissions.split(',')
        if roles is not None:
            payload['roles'] = roles.split(',')
        url = self.endpoint+'elaap/api/v1/permissions/'+_id
        request = requests.put(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def perm_search(self, _id, scopes, permissions, roles):
        params = {}
        if _id is not None:
            params['_id'] = _id
        if scopes is not None:
            params['scopes'] = scopes
        if permissions is not None:
            params['permissions'] = permissions
        if roles is not None:
            params['roles'] = roles
        url = self.endpoint+'elaap/api/v1/permissions/_search'
        request = requests.get(url, params=params, headers=self.session)
        for result in request.json()['results']:
            print(result)

    def perm_add_perms(self, _id, permissions):
        payload = permissions.split(',')
        url = self.endpoint+'elaap/api/v1/permissions/'+_id+'/permissions'
        request = requests.put(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def perm_del_perms(self, _id, permissions):
        payload = permissions.split(',')
        url = self.endpoint+'elaap/api/v1/permissions/'+_id+'/permissions'
        request = requests.delete(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def perm_add_roles(self, _id, roles):
        payload = roles.split(',')
        url = self.endpoint+'elaap/api/v1/permissions/'+_id+'/roles'
        request = requests.put(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def perm_del_roles(self, _id, roles):
        payload = roles.split(',')
        url = self.endpoint+'elaap/api/v1/permissions/'+_id+'/roles'
        request = requests.delete(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def roles_add(self, _id, description, users):
        payload = {
            '_id': _id,
            'description': description,
            'users': users.split(',')
        }
        url = self.endpoint+'elaap/api/v1/roles'
        request = requests.post(url, json=payload, headers=self.session)
        if request.status_code == 201:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def roles_del(self, _id):
        url = self.endpoint+'elaap/api/v1/roles/'+_id
        request = requests.delete(url, headers=self.session)
        if request.status_code == 200:
            print('role deleted')
        else:
            print(request.json())
            sys.exit(1)

    def roles_get(self, _id):
        url = self.endpoint+'elaap/api/v1/roles/'+_id
        request = requests.get(url, headers=self.session)
        if request.status_code == 202:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def roles_update(self, _id, description, users):
        payload = {}
        if description is not None:
            payload['description'] = description
        if users is not None:
            payload['users'] = users.split(',')
        url = self.endpoint+'elaap/api/v1/roles/'+_id
        request = requests.put(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def roles_search(self, _id, users):
        params = {}
        if _id is not None:
            params['_id'] = _id
        if users is not None:
            params['users'] = users
        url = self.endpoint+'elaap/api/v1/roles/_search'
        request = requests.get(url, params=params, headers=self.session)
        for result in request.json()['results']:
            print(result)

    def roles_add_users(self, _id, users):
        payload = users.split(',')
        url = self.endpoint+'elaap/api/v1/roles/'+_id+'/users'
        request = requests.put(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def roles_del_users(self, _id, users):
        payload = users.split(',')
        url = self.endpoint+'elaap/api/v1/roles/'+_id+'/users'
        request = requests.delete(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def users_add(self, _id, admin, email, name, password):
        payload = {
            '_id': _id,
            'admin': admin,
            'email': email,
            'name': name,
            'password': password
        }
        url = self.endpoint+'elaap/api/v1/users'
        request = requests.post(url, json=payload, headers=self.session)
        if request.status_code == 201:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def users_del(self, _id):
        url = self.endpoint+'elaap/api/v1/users/'+_id
        request = requests.delete(url, headers=self.session)
        if request.status_code == 200:
            print('user deleted')
        else:
            print(request.json())
            sys.exit(1)

    def users_get(self, _id):
        url = self.endpoint+'elaap/api/v1/users/'+_id
        request = requests.get(url, headers=self.session)
        if request.status_code == 202:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def users_update(self, _id, admin, email, name, password):
        payload = {}
        if admin is not None:
            payload['admin'] = admin
        if email is not None:
            payload['email'] = email
        if name is not None:
            payload['name'] = name
        if password is not None:
            payload['password'] = password
        url = self.endpoint+'elaap/api/v1/users/'+_id
        request = requests.put(url, json=payload, headers=self.session)
        if request.status_code == 200:
            print(request.json())
        else:
            print(request.json())
            sys.exit(1)

    def users_search(self, _id):
        params = {}
        if _id is not None:
            params['_id'] = _id
        url = self.endpoint+'elaap/api/v1/users/_search'
        request = requests.get(url, params=params, headers=self.session)
        for result in request.json()['results']:
            print(result)
