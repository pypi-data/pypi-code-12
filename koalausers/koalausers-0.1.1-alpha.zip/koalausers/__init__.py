# -*- coding: utf-8 -*-
"""
    koalausers.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    User account package. Provides a basic user model for login purposes.

    This model is adapted from webapp2_extras.appengine.auth.models

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import koalacore
from blinker import signal
from google.appengine.ext import ndb
from google.appengine.ext import deferred


__author__ = 'Matt Badger'


class BaseUser(koalacore.Resource):
    username = koalacore.ResourceProperty(title=u'Username', unique=True, force_lowercase=True)
    email_address = koalacore.ResourceProperty(title=u'Email', unique=True, force_lowercase=True)
    first_name = koalacore.ResourceProperty(title=u'First Name')
    last_name = koalacore.ResourceProperty(title=u'Last Name')
    password = koalacore.ResourceProperty(title=u'Password', strip_whitespace=False)
    raw_password = koalacore.ResourceProperty(title=u'Raw Password', strip_whitespace=False)   # Remove?
    language_preference = koalacore.ResourceProperty(title=u'Language Preference')
    recovery_email_address = koalacore.ResourceProperty(title=u'Recovery Email', unique=True, force_lowercase=True)
    email_address_verified = koalacore.ResourceProperty(title=u'Email Verified', default=False)
    recovery_email_address_verified = koalacore.ResourceProperty(title=u'Recovery Email Verified', default=False)

    def __init__(self, password=None, raw_password=None, **kwargs):
        assert password or raw_password, 'Must supply either hashed password or raw password to be hashed.'

        if raw_password:
            kwargs['password'] = self._hash_password(raw_password=raw_password)
        else:
            kwargs['password'] = password

        super(BaseUser, self).__init__(**kwargs)

    @staticmethod
    def _hash_password(raw_password):
        return koalacore.generate_password_hash(raw_password, salt_length=12)

    @property
    def auth_ids(self):
        return [self.username, self.email_address]

    def change_password(self, raw_password):
        """Sets the password for the current user

        :param raw_password:
            The raw password which will be hashed and stored
        """
        self.password = self._hash_password(raw_password=raw_password)

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.text_field(name='fuzzy_username',
                                                value=koalacore.generate_autocomplete_tokens(original_string=self.username)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_email_address',
                                                value=koalacore.generate_autocomplete_tokens(original_string=self.email_address)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_recovery_email_address',
                                                value=koalacore.generate_autocomplete_tokens(original_string=self.recovery_email_address)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_first_name',
                                                value=koalacore.generate_autocomplete_tokens(original_string=self.first_name)),
            koalacore.GAESearchInterface.text_field(name='fuzzy_last_name',
                                                value=koalacore.generate_autocomplete_tokens(original_string=self.last_name)),
            koalacore.GAESearchInterface.date_field(name='created', value=self.created),
            koalacore.GAESearchInterface.date_field(name='updated', value=self.updated),
            koalacore.GAESearchInterface.atom_field(name='username', value=self.username),
            koalacore.GAESearchInterface.atom_field(name='email_address', value=self.email_address),
            koalacore.GAESearchInterface.atom_field(name='recovery_email_address', value=self.recovery_email_address),
            koalacore.GAESearchInterface.atom_field(name='first_name', value=self.first_name),
            koalacore.GAESearchInterface.atom_field(name='last_name', value=self.last_name),
            koalacore.GAESearchInterface.atom_field(name='language_preference', value=self.language_preference),
            koalacore.GAESearchInterface.atom_field(name='email_address_verified',
                                                value='Y' if self.email_address_verified else 'N'),
            koalacore.GAESearchInterface.atom_field(name='recovery_email_address_verified',
                                                value='Y' if self.recovery_email_address_verified else 'N'),
        ]


class BaseUserGroup(koalacore.Resource):
    group_uid = koalacore.ResourceProperty(title=u'Group UID', immutable=True)
    user_uid = koalacore.ResourceProperty(title=u'User UID', immutable=True)
    group_name = koalacore.ResourceProperty(title=u'Group Name')

    def to_search_doc(self):
        return [
            koalacore.GAESearchInterface.atom_field(name='group_uid', value=self.group_uid),
            koalacore.GAESearchInterface.atom_field(name='group_name', value=self.group_name),
            koalacore.GAESearchInterface.atom_field(name='user_uid', value=self.user_uid),
        ]


class SessionStorage(object):
    """
    Simply set properties which can then be saved and retrieved at any time. Keep it small - this is not intended to be
    a cache of frequent data.
    """
    pass


class User(BaseUser):
    groups = koalacore.ResourceProperty(title=u'Groups')
    session = koalacore.ResourceProperty(title=u'Session')
    permissions = koalacore.ResourceProperty(title=u'Permissions')

    def __init__(self, **kwargs):
        # Unfortunately, we can't set mutable defaults on a resource property
        if 'groups' not in kwargs or kwargs['groups'] is None:
            # Groups should be stored in the format group_uid: group_name
            kwargs['groups'] = {}

        if 'session' not in kwargs or kwargs['session'] is None:
            kwargs['session'] = SessionStorage()

        if 'permissions' not in kwargs or kwargs['permissions'] is None:
            if 'roles' in kwargs:
                roles = kwargs['roles']
                del kwargs['roles']
            else:
                roles = {'user'}

            if 'acl' in kwargs:
                acl = kwargs['acl']
                del kwargs['acl']
            else:
                acl = {'self': {'read_profile', 'update_profile', 'change_password'}}

            kwargs['permissions'] = koalacore.PermissionsStorage(roles=roles, acl=acl)

        super(User, self).__init__(**kwargs)

    def to_search_doc(self):
        base_fields = super(User, self).to_search_doc()

        roles = [koalacore.GAESearchInterface.atom_field(name='role', value=role) for role in self.permissions.roles]
        groups = [koalacore.GAESearchInterface.atom_field(name='group_uid', value=group_uid) for group_uid, details in self.groups.iteritems()]
        group_key_ids = [koalacore.GAESearchInterface.atom_field(name='group_key_id', value=str(ndb.Key(urlsafe=group_uid).id())) for group_uid, details in self.groups.iteritems()]

        return base_fields + roles + groups + group_key_ids


class UserGroup(BaseUserGroup):
    action_set = koalacore.ResourceProperty(title=u'ACL')


class BaseNDBUserModel(koalacore.NDBResource):
    """
    User model to store authentication credentials or authorization ids.

    """
    auth_ids = ndb.ComputedProperty(func=lambda self: [self.username, self.email_address], repeated=True)
    password = ndb.StringProperty('up', indexed=False)

    username = ndb.StringProperty('un', indexed=False)
    email_address = ndb.StringProperty('upe', indexed=False)
    email_address_verified = ndb.BooleanProperty('upev', default=False, indexed=False)
    recovery_email_address = ndb.StringProperty('upre', indexed=False)
    recovery_email_address_verified = ndb.BooleanProperty('uprev', default=False, indexed=False)
    first_name = ndb.StringProperty('ufn', indexed=False)
    last_name = ndb.StringProperty('uln', indexed=False)
    language_preference = ndb.StringProperty('ulp', indexed=False)


class BaseNDBUserGroupModel(koalacore.NDBResource):
    """
    User group model to store relationship between user and group

    """
    group_uid = ndb.KeyProperty('ugguid', indexed=True)
    group_name = ndb.StringProperty('uggn', indexed=False)   # We don't know what the group is, so a name must be set


class NDBUserModel(BaseNDBUserModel):
    """
    User model with support for groups, permissions and session storage.
    """
    groups = ndb.PickleProperty('ugc', indexed=False)
    session = ndb.PickleProperty('usc', indexed=False)
    permissions = ndb.PickleProperty('uacl', indexed=False)


class NDBUserGroupModel(BaseNDBUserGroupModel):
    """
    Extends user group model to include an acl for granting additional permissions to a user
    """
    action_set = ndb.PickleProperty('ugacl', indexed=False)


class UserNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBUserModel
    _resource_object = User

    @classmethod
    def _internal_query_by_auth_id(cls, auth_id):
        op_result = cls._datastore_model.query(cls._datastore_model.auth_ids == auth_id).get_async()
        op_result.method = 'get_async'

        return op_result

    @classmethod
    def query_by_auth_id_async(cls, auth_id):
        """
        This is just to keep consistency with the Koala datastore class. It isn't actually necessary because we don't
        have to do any conversion on the method args.

        :param auth_id:
        :returns future:
        """
        return cls._internal_query_by_auth_id(auth_id=auth_id)

    @classmethod
    def query_by_auth_id(cls, auth_id):
        """
        Wrapper around query_by_auth_id_async to automatically resolve async future. May be overridden.

        :param auth_id:
        :returns resource_object, or None:
        """
        entity_future = cls.query_by_auth_id_async(auth_id=auth_id)
        return cls.parse_get_async_result(entity_future)


class UserGroupNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBUserGroupModel
    _resource_object = UserGroup

    @classmethod
    def _convert_resource_object_to_datastore_model(cls, resource_object):
        """
        Need to override the default conversion function as we need to do some funky ancestor key setup and indexing.
        """
        model_kwargs = {}

        if resource_object.uid:
            model_kwargs['key'] = cls._convert_string_to_ndb_key(datastore_key=resource_object.uid)
        else:
            model_kwargs['parent'] = cls._convert_string_to_ndb_key(datastore_key=resource_object.user_uid)

        model_kwargs['group_uid'] = cls._convert_string_to_ndb_key(datastore_key=resource_object.group_uid)
        model_kwargs['group_name'] = resource_object.group_name
        model_kwargs['action_set'] = resource_object.action_set

        if resource_object.created:
            model_kwargs['created'] = resource_object.created

        return cls._datastore_model(**model_kwargs)

    @classmethod
    def _convert_datastore_model_to_resource_object(cls, datastore_model):
        """
        Convert native ndb model into resource object.

        :param datastore_model:
        :returns resource_object:
        """
        resource_kwargs = {
            'uid': cls._convert_ndb_key_to_string(datastore_key=datastore_model.key),
            'user_uid': cls._convert_ndb_key_to_string(datastore_key=datastore_model.key.parent()),
            'group_uid': cls._convert_ndb_key_to_string(datastore_key=datastore_model.group_uid),
            'group_name': datastore_model.group_name,
            'action_set': datastore_model.action_set,
            'created': datastore_model.created,
            'updated': datastore_model.updated,
        }

        return cls._resource_object(**resource_kwargs)

    @classmethod
    def get_future_result(cls, future):
        """
        Helper function to call the relevant future resolver method based on the 'method' property of future.

        :param future:
        :raises AttributeError (if future does not have a method property set:
        :returns result of future:
        """
        method = future.method

        if method == 'insert_async':
            return cls.parse_insert_async_result(future)
        elif method == 'get_async':
            return cls.parse_get_async_result(future)
        elif method == 'update_async':
            return cls.parse_update_async_result(future)
        elif method == 'patch_async':
            return cls.parse_patch_async_result(future)
        elif method == 'delete_async':
            return cls.parse_delete_async_result(future)
        elif method == 'list_async':
            return cls.parse_list_async_result(future)
        elif method == 'get_group_users_async':
            return cls.parse_get_group_users_async_result(future)

    @classmethod
    def parse_get_group_users_async_result(cls, future):
        results = future.get_result()
        # For result in results, get parent and then return urlsafe version
        return [result.parent().urlsafe() for result in results]

    @classmethod
    def _internal_get_user_groups(cls, user_uid, **kwargs):
        # TODO: query cursor support
        op_result = cls._datastore_model.query(ancestor=user_uid).fetch_async()
        op_result.method = 'get_async'

        return op_result

    @classmethod
    def get_user_groups_async(cls, user_uid, **kwargs):
        """
        This is just to keep consistency with the Koala datastore class. It isn't actually necessary because we don't
        have to do any conversion on the method args.

        :param user_uid:
        :returns future:
        """
        return cls._internal_get_user_groups(user_uid=cls._convert_string_to_ndb_key(datastore_key=user_uid), **kwargs)

    @classmethod
    def get_user_groups(cls, user_uid, **kwargs):
        """
        Wrapper around get_user_groups_async to automatically resolve async future. May be overridden.

        :param user_uid:
        :returns resource_object, or None:
        """
        entity_future = cls.get_user_groups_async(user_uid=user_uid)
        return cls.get_future_result(entity_future)

    @classmethod
    def _internal_get_user_group(cls, user_uid, group_uid, **kwargs):
        # There should only ever be one result to this query, if any
        op_result = cls._datastore_model.query(cls._datastore_model.group_uid == group_uid, ancestor=user_uid).get_async()
        op_result.method = 'get_async'

        return op_result

    @classmethod
    def get_user_group_async(cls, user_uid, group_uid, **kwargs):
        """
        This is just to keep consistency with the Koala datastore class. It isn't actually necessary because we don't
        have to do any conversion on the method args.

        :param user_uid:
        :param group_uid:
        :returns future:
        """
        return cls._internal_get_user_group(user_uid=cls._convert_string_to_ndb_key(datastore_key=user_uid),
                                            group_uid=cls._convert_string_to_ndb_key(datastore_key=group_uid), **kwargs)

    @classmethod
    def get_user_group(cls, user_uid, group_uid, **kwargs):
        """
        Wrapper around get_user_group_async to automatically resolve async future. May be overridden.

        :param user_uid:
        :param group_uid:
        :returns resource_object, or None:
        """
        entity_future = cls.get_user_group_async(user_uid=user_uid, group_uid=group_uid, **kwargs)
        return cls.get_future_result(entity_future)

    @classmethod
    def _internal_get_group_users(cls, group_uid, **kwargs):
        # TODO: query cursor support
        op_result = cls._datastore_model.query(cls._datastore_model.group_uid == group_uid).fetch_async(keys_only=True)
        op_result.method = 'get_group_users_async'

        return op_result

    @classmethod
    def get_group_users_async(cls, group_uid, **kwargs):
        """
        This is just to keep consistency with the Koala datastore class. It isn't actually necessary because we don't
        have to do any conversion on the method args.

        :param group_uid:
        :returns future:
        """
        return cls._internal_get_group_users(group_uid=cls._convert_string_to_ndb_key(datastore_key=group_uid), **kwargs)

    @classmethod
    def get_group_users(cls, group_uid, **kwargs):
        """
        Wrapper around get_group_users_async to automatically resolve async future. May be overridden.

        :param group_uid:
        :returns resource_object, or None:
        """
        entity_future = cls.get_group_users_async(group_uid=group_uid, **kwargs)
        return cls.get_future_result(entity_future)


class UserSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'users'
    _resource_object = User


class UserGroupSearchInterface(koalacore.GAESearchInterface):
    _index_name = 'user_groups'
    _resource_object = UserGroup


class Users(koalacore.BaseAPI):
    _api_name = 'users'
    _api_model = User
    _datastore_interface = UserNDBInterface
    _search_interface = UserSearchInterface

    @classmethod
    def get_by_auth_id(cls, auth_id):
        user = cls._datastore_interface.query_by_auth_id(auth_id=auth_id)
        signal('get.hook').send(cls, user=user)
        return user

    @classmethod
    def get_by_auth_details_and_verify(cls, auth_id, password):
        user = cls._datastore_interface.query_by_auth_id(auth_id=auth_id)
        if not user:
            signal('verify_auth_failed_auth_id.hook').send(cls, auth_id=auth_id)
            return False, u'Invalid username or email address'

        if not koalacore.check_password_hash(pwhash=user.password, password=password):
            signal('verify_auth_failed_password.hook').send(cls, auth_id=auth_id)
            return False, u'Password does not match'

        signal('verified_auth.hook').send(cls, user=user)
        signal('get.hook').send(cls, user=user)
        return True, user


class UserGroups(koalacore.BaseAPI):
    _api_name = 'user_groups'
    _api_model = UserGroup
    _datastore_interface = UserGroupNDBInterface
    _search_interface = UserGroupSearchInterface

    @classmethod
    def get_by_group_uid(cls, user_uid, group_uid, **kwargs):
        if signal('pre_get_by_group_uid').has_receivers_for(cls):
            signal('pre_get_by_group_uid').send(cls, user_uid=user_uid, group_uid=group_uid, **kwargs)

        resource = cls._datastore_interface.get_user_group(user_uid=user_uid, group_uid=group_uid, **kwargs)

        if signal('post_get_by_group_uid').has_receivers_for(cls):
            signal('post_get_by_group_uid').send(cls, result=resource, user_uid=user_uid, group_uid=group_uid, **kwargs)

        return resource

    @classmethod
    def delete(cls, resource_uid, **kwargs):
        """
        This override is just to add documentation. Basically, this method will *only* delete the UserGroup entity from
        the datastore. It will not update the related user. There are almost no instances where this method is useful,
        but it is left in for consistency.

        :param resource_uid:
        :param kwargs:
        :return:
        """
        super(UserGroups, cls).delete(resource_uid=resource_uid, **kwargs)

    @classmethod
    def delete_by_group_uid(cls, user_uid, group_uid, **kwargs):
        """
        Delete a UserGroup entity and also update the referenced User.

        :param user_uid:
        :param group_uid:
        :param kwargs:
        :return:
        """
        if signal('pre_delete_by_group_uid').has_receivers_for(cls):
            signal('pre_delete_by_group_uid').send(cls, user_uid=user_uid, group_uid=group_uid, **kwargs)

        user_group = cls._datastore_interface.get_user_group(user_uid=user_uid, group_uid=group_uid, **kwargs)

        if not user_group:
            raise ValueError(u'User Group not found')

        cls._datastore_interface.delete(resource_uid=user_group.uid, **kwargs)
        deferred.defer(cls._delete_search_index, resource_uid=user_group.uid, _queue='search-index-update')

        if signal('post_delete_by_group_uid').has_receivers_for(cls):
            signal('post_delete_by_group_uid').send(cls, result=None, resource_uid=user_group.uid, user_uid=user_uid, group_uid=group_uid, **kwargs)

    @classmethod
    def get_user_groups(cls, user_uid, **kwargs):
        if user_uid is None:
            return None   # We should probably raise an error instead
        # returns user_group objects for the given user_uid
        user_groups = cls._datastore_interface.get_user_groups(user_uid=user_uid)
        signal('get_user_groups.hook').send(cls, user_groups=user_groups)
        return user_groups

    @classmethod
    def get_group_users(cls, group_uid, **kwargs):
        if group_uid is None:
            return None   # We should probably raise an error instead
        # Returns a list of user_uids for the specified group
        group_users = cls._datastore_interface.get_group_users(group_uid=group_uid)
        signal('get_group_users.hook').send(cls, user_groups=group_users)
        return group_users


def _defer_update_change_group(user_group_uid, **kwargs):
    # If there is no resource_uid then we should abort the task
    if not user_group_uid:
        raise deferred.PermanentTaskFailure

    user_group_future = UserGroupNDBInterface.get_async(resource_uid=user_group_uid)

    user_group_key = UserGroupNDBInterface._convert_string_to_ndb_key(datastore_key=user_group_uid)
    user_uid = user_group_key.parent().urlsafe()

    user_future = UserNDBInterface.get_async(resource_uid=user_uid)

    user_group = UserGroupNDBInterface.parse_get_async_result(future=user_group_future)
    user = UserNDBInterface.parse_get_async_result(future=user_future)

    user.groups[user_group.group_uid] = user_group.group_name
    user.permissions.set_acl_entry(resource_uid=user_group.group_uid, actions_set=user_group.action_set)

    UserNDBInterface.update(resource_object=user)


def defer_user_groups_update(sender, result, **kwargs):
    if result:
        deferred.defer(_defer_update_change_group, user_group_uid=result, _queue='deferredwork')


signal('post_insert').connect(defer_user_groups_update, sender=UserGroups)
signal('post_update').connect(defer_user_groups_update, sender=UserGroups)


def _defer_update_remove_group(user_uid, group_uid, **kwargs):
    # If there is no resource_uid then we should abort the task
    if not user_uid or not group_uid:
        raise deferred.PermanentTaskFailure

    user = UserNDBInterface.get(resource_uid=user_uid)

    del user.groups[group_uid]
    user.permissions.remove_acl_entry(resource_uid=group_uid)

    UserNDBInterface.update(resource_object=user)


def defer_user_groups_delete(sender, user_uid, group_uid, **kwargs):
    if user_uid and group_uid:
        deferred.defer(_defer_update_remove_group, user_uid=user_uid, group_uid=group_uid, _queue='deferredwork')


# We disabled update on delete because we won't know the group_uid to delete from use at this point.
# signal('post_delete').connect(defer_user_groups_delete, sender=UserGroups)
signal('post_delete_by_group_uid').connect(defer_user_groups_delete, sender=UserGroups)
