#!/usr/bin/env python3
"""
Slack slash-command interpreter

Managed semi-secure user groups for Slack.

You can configure this, so that a user that is in one private group can request,
automatically, to be added to other private groups.

    Copyright (c) 2016, Paul Traina
    All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import re

import requests
import slacker
from slacker.utils import get_item_id_by_name

class ConfigError(Exception):
    """ Program configuration error """
    pass

class UsageError(Exception):
    """ Program configuration error """
    pass

class SlackGM(object):
    """ Slack Group Manager Interface """
    def __init__(self, config, users, admin=False):
        """ Initialize the information we're going to need from Slack """
        self.config = config
        self.target_users = users
        self.admin = admin
        self.slacker = None
        self.team_users = None
        self.team_groups = None
        self.team_channels = None

    def _user_id(self, name):
        """ Return the Slack UID of username """
        return  get_item_id_by_name(self.team_users, name)

    def _user_name(self, uid):
        """ Return the Slack username of UID """
        for user in self.team_users:
            if uid == user['id']:
                return user['name']

    def _group_id(self, name):
        """ Return the Slack GID of a groupname """
        return  get_item_id_by_name(self.team_groups, name)

    def _channel_members(self, name):
        """ Return a list of UIDs for this public channels's membership """
        for channel in self.team_channels:
            if name == channel['name']:
                return channel['members']

    def _group_members(self, name):
        """ Return a list of UIDs for this private groups's membership """
        for group in self.team_groups:
            if name == group['name']:
                return group['members']

    def _group_adduser(self, group, user):
        """ Add a user to a given group -- no permission checks are done here """
        try:
            self.slacker.groups.invite(self._group_id(group), self._user_id(user))
        except slacker.Error as err:
            raise slacker.Error("Unable to add {} to {}: {}".format(user, group, err))

    def available_groups(self, user):
        """ Get a list of group names available to this user """
        uid = self._user_id(user)

        templates = set()
        for group in self.team_groups:
            if group['name'] in self.config['groups'] and \
                    (self.admin or uid in group['members']):
                for template in self.config['groups'][group['name']]:
                    templates.add(template)

        groups = []
        for group in self.team_groups:
            for template in templates:
                match = re.match(template, group['name'])
                if match:
                    groups.append(group)

        return groups

    def _disallowed_users(self, audit_group):
        """ Look through the group membership and return a list of unauthorized usernames """
        allowed_uids = []
        for master, children in self.config['groups'].items():
            for child in children:
                if re.match(child, audit_group):
                    allowed_uids += self._group_members(master)
        if not allowed_uids:    # no master group found for this group, play it safe
            return []
        disallowed_uids = list(set(self._group_members(audit_group))-set(allowed_uids))
        return [self._user_name(uid) for uid in disallowed_uids]

    def group_audit(self, dummy_arguments):
        """ Look at all groups to determine if any disallowed users """
        empty = True
        for group in self.team_groups:
            disallowed = self._disallowed_users(group['name'])
            if disallowed:
                if empty:
                    print('Groups with unauthorized members:')
                    empty = False
                print('{}: {}'.format(group['name'], ', '.join(sorted(disallowed))))
        if empty:
            print('No groups with unauthorized members')

    def group_audit_cleanup(self, specified_groups):
        """ Remove any disallowed users (use audit get list) from specified groups (or all) """
        for group in self.team_groups:
            if not specified_groups or group['name'] not in specified_groups:
                for user in sorted(self._disallowed_users(group['name'])):
                    print('Removing {} from {}'.format(user, group['name']))
                    self.slacker.groups.kick(group['id'], self._user_id(user))

    def group_bulkadd(self, arguments):
        """
        Add all members from one group to another group.

        From may be a private group or public channel.
        To must be a private group.
        """
        try:
            group_from = arguments[0]
            group_to = arguments[1]
        except IndexError:
            raise UsageError('must specify from and to group')

        try:
            group_limit = arguments[2]
        except IndexError:
            group_limit = None

        new_users = self._group_members(group_from) or self._channel_members(group_from)
        if not new_users:
            raise UsageError('{}: invalid group or channel'.format(group_from))

        cur_users = self._group_members(group_to)
        if not cur_users:
            raise UsageError('{}: invalid group'.format(group_to))

        add_uids = list(set(new_users) - set(cur_users))
        if not add_uids:
            print("No users in {} that aren't in {}".format(group_from, group_to))

        if group_limit:
            limit_users = self._group_members(group_limit)
            if not limit_users:
                raise UsageError('{}: invalid group'.format(group_limit))
            add_uids = list(set(add_uids) & set(limit_users))


        add_users = sorted([self._user_name(uid) for uid in add_uids])

        print('Adding to {}: {}'.format(group_to, ', '.join(add_users)))
        for user in add_users:
            self._group_adduser(group_to, user)

    def group_compare(self, arguments):
        """
        Print a comparison of membership between two groups or channels.

        From and to may be either private groups or public channels.
        """
        try:
            group_a = arguments[0]
            group_b = arguments[1]
        except IndexError:
            raise UsageError('must specify two groups or channels')

        members_a = self._group_members(group_a) or self._channel_members(group_a)
        if not members_a:
            raise UsageError('{}: empty/invalid group or channel'.format(group_a))

        members_b = self._group_members(group_b) or self._channel_members(group_b)
        if not members_b:
            raise UsageError('{}: empty/invalid group or channels'.format(group_b))

        a_not_b = sorted([self._user_name(uid) for uid in list(set(members_a) - set(members_b))])
        b_not_a = sorted([self._user_name(uid) for uid in list(set(members_b) - set(members_a))])
        b_and_a = sorted([self._user_name(uid) for uid in list(set(members_b) & set(members_a))])

        print("Members in {} but not {}: {}".format(group_a, group_b, ', '.join(a_not_b)))
        print("Members in {} but not {}: {}".format(group_b, group_a, ', '.join(b_not_a)))
        print("Members in both {} and {}: {}".format(group_a, group_b, ', '.join(b_and_a)))

    def group_list(self, arguments):
        """ Print a list of groups and purposes that user may join """
        if not self.target_users:
            raise ConfigError('no user context')
        include_id = arguments and arguments[0] == 'id'
        for user in self.target_users:
            groups = self.available_groups(user)
            if not groups:
                print('{} has no groups available'.format(user))
            else:
                for group in groups:
                    if 'purpose' in group and 'value' in group['purpose']:
                        purpose = ' - ' + group['purpose']['value']
                    else:
                        purpose = ''
                    if include_id:
                        print("{} ({}){}".format(group['name'], group['id'], purpose))
                    else:
                        print(group['name'] + purpose)

    def group_add(self, arguments):
        """ Process group addition requests -- check permissions """
        if not arguments:
            raise UsageError("missing group name(s)")
        for user in self.target_users:
            available = sorted([group['name'] for group in self.available_groups(user)])
            for group in arguments:
                if group in available:
                    self._group_adduser(group, user)
                    print('{} added to {}'.format(user, group))
                else:
                    print('{} not added to {}: unrecognized group'.format(user, group))

    def group_leave(self, groups):
        """ Remove groupmgr from the specified groups (use with care!) """
        if not groups:
            raise UsageError("missing group name(s)")
        for group in self.team_groups:
            if group['name'] in groups:
                print('Leaving {}'.format(group['name']))
                self.slacker.groups.leave(group['id'])

    def usage(self, dummy_arguments=None):
        """ Print command usage """
        print("Available commands:")
        for command in sorted(self._commands):
            if self.admin or \
                    'admin-required' not in self._commands[command].get('options', []):
                print('{}: {}'.format(command, self._commands[command]['help']))

    _commands = {
        'add': {
            'function': group_add,
            'help': 'add yourself to a group'
        },
        'list': {
            'function': group_list,
            'help': 'list available groups'
        },
        'add-membership': {
            'function': group_bulkadd,
            'help': 'add members from <fromgroup> to <togroup> [<limitgroup>]',
            'options': ['admin-required'],
        },
        'compare-membership': {
            'function': group_compare,
            'help': 'add compare from <group/channel> with <group/channel>',
            'options': ['admin-required'],
        },
        'audit': {
            'function': group_audit,
            'help': 'audit available groups',
            'options': ['admin-required']
        },
        'audit-cleanup': {
            'function': group_audit_cleanup,
            'help': 'remove all users failing the group audit (use with care!)',
            'options': ['admin-required']
        },
        'leave': {
            'function': group_leave,
            'help': 'remove group manager from specified group',
            'options': ['admin-required']
        },
        'help': {
            'function': usage,
            'help': 'help on available commands'
        }
    }

    def process_command(self, command, arguments):
        """ Process a parsed command """
        if not command:
            raise UsageError("no command specified")

        if command not in self._commands or \
                (not self.admin and \
                 'admin-required' in self._commands[command].get('options', [])):
            raise UsageError("{}: unrecognized command".format(command))

        self.slacker = slacker.Slacker(self.config['api_token'])
        self.team_users = self.slacker.users.list().body['members']
        self.team_groups = self.slacker.groups.list(exclude_archived=1).body['groups']
        self.team_channels = self.slacker.channels.list(exclude_archived=1).body['channels']

        self._commands[command]['function'](self, arguments)
