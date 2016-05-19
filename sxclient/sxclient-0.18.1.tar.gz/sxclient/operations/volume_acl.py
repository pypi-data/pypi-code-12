'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from collections import defaultdict
from itertools import product

from sxclient.operations.base import BaseOperation
from sxclient.models.query_parameters import QueryParameters


__all__ = ['GetVolumeACL', 'UpdateVolumeACL', 'SetVolumeACL']


def _dict_of_lists_to_tuples(dict_of_lists):
    for key, value_list in dict_of_lists.iteritems():
        for value in value_list:
            yield key, value


class GetVolumeACL(BaseOperation):
    '''
    Get volume's access control list.

    Required access: user with any kind of permissions for the volume.

    Query specific parameters:
      - volume -- name of the volume to get ACL of
    '''

    def _generate_query_params(self, volume):
        return QueryParameters(
            sx_verb='GET',
            path_items=[volume],
            bool_params={'manager'},
            dict_params={'o': 'acl'}
        )


class UpdateVolumeACL(BaseOperation):
    '''
    Update volume's access control list.

    Required access: volume manager.

    Query specific parameters:
      - volume -- name of the volume to change ACL of
      - actions -- dictionary consisting of at least one of 'grant-read',
        'grant-write', 'grant-manager', 'revoke-read', 'revoke-write',
        'revoke-manager' as keys, each having a list of user names as a value.
        Actions described in the dictionary will be applied on top of the
        existing ACL.
    '''

    def _generate_body(self, volume, actions):
        return actions

    def _generate_query_params(self, volume, actions):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=[volume],
            dict_params={'o': 'acl'}
        )


class SetVolumeACL(UpdateVolumeACL):
    '''
    Set volume's access control list, replacing the permissions for the
    specified users.

    Required access: volume manager.

    Query specific parameters:
      - volume -- name of the volume to change ACL of
      - permissions -- dictionary describing new permission sets for a group of
        users, containing usernames as keys and lists of permission names
        ('read', 'write', 'manager') as values.
    '''

    def _get_entries(self, users, permissions):
        perms = ('read', 'write', 'manager')
        possible_entries = product(users, perms)
        new_entries = set(_dict_of_lists_to_tuples(permissions))
        return possible_entries, new_entries

    def _generate_actions(self, possible_entries, new_entries):
        actions = defaultdict(set)
        for entry in possible_entries:
            user, perm = entry
            if entry in new_entries:
                action = 'grant-'
            else:
                action = 'revoke-'
            actions[action + perm].add(user)

        return {
            key: list(value) for key, value in actions.iteritems()
        }

    def call(self, volume, permissions):
        users = permissions.iterkeys()
        possible_entries, new_entries = self._get_entries(users, permissions)
        actions = self._generate_actions(possible_entries, new_entries)
        return super(SetVolumeACL, self).call(volume, actions)
