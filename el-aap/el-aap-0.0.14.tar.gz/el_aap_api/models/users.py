__author__ = 'schlitzer'

import logging

from bottle import request
from passlib.hash import pbkdf2_sha512
import pymongo
import pymongo.errors

from el_aap_api.models.mixins import FilterMixIn, PaginationSkipMixIn, ProjectionMixIn, SortMixIn
from el_aap_api.errors import *


class Users(FilterMixIn, PaginationSkipMixIn, ProjectionMixIn, SortMixIn):
    def __init__(self, coll):
        self.projection_fields = {
            '_id': 1,
            'admin': 1,
            'email': 1,
            'name': 1
        }
        self.sort_fields = [
            ('_id', pymongo.ASCENDING),
            ('email', pymongo.ASCENDING),
            ('name', pymongo.ASCENDING),
            ('admin', pymongo.ASCENDING)
        ]
        self._coll = coll
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def _password(self, password):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} hashing password'.format(request_id))
        return pbkdf2_sha512.encrypt(password, rounds=100000, salt_size=32)

    @method_wrapper
    def check_credentials(self, credentials):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} validating credentials for user {1}'.format(
            request_id, credentials['user']))
        password = self._coll.find_one(
                filter={'_id': credentials['user']},
                projection={'_id': 0, 'password': 1}
        )
        if not password:
            self.log.warning('{0} failed validating credentials, user {1} not found'.format(
                request_id, credentials['user']))
            raise AuthenticationError
        if not pbkdf2_sha512.verify(credentials['password'], password['password']):
            self.log.warning('{0} failed validating credentials, password wrong for user {1}'.format(
                request_id, credentials['user']))
            raise AuthenticationError

        self.log.info('{0} success validating credentials for user {1}'.format(
            request_id, credentials['user']))
        return credentials['user']

    @method_wrapper
    def check_ids(self, _ids):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} checking if user ids {1} exist'.format(request_id, _ids))
        count = self._coll.find(
            filter={'_id': {'$in': _ids}},
            projection={'id': 1}).count()
        return len(_ids) == count

    @method_wrapper
    def create(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} creating new user resource {1}'.format(request_id, user['_id']))
        user['password'] = self._password(user['password'])
        try:
            self._coll.insert_one(user)
        except pymongo.errors.DuplicateKeyError:
            self.log.warning('{0} user resource {1} already exists'.format(request_id, user['_id']))
            raise DuplicateResource(user['_id'])
        self.log.info('{0} success creating new user resource {1}'.format(request_id, user['_id']))
        return self.get(user['_id'])

    @method_wrapper
    def delete(self, _id):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} deleting user resource {1}'.format(request_id, _id))
        result = self._coll.delete_one(filter={'_id': _id})
        if result.deleted_count is 0:
            self.log.warning('{0} user resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success deleting user resource {1}'.format(request_id, _id))
        return

    @method_wrapper
    def get(self, _id, fields=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} fetching user resource {1}'.format(request_id, _id))
        result = self._coll.find_one(
            filter={'_id': _id},
            projection=self._projection(fields)
        )
        if result is None:
            self.log.warning('{0} user resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success fetching user resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def is_admin(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} checking if user {1} is admin'.format(request_id, user))
        resource = self.get(user, fields='admin')
        if not resource['admin']:
            self.log.debug('{0} user {1} is no admin'.format(request_id, user))
            return False
        else:
            self.log.debug('{0} user {1} is admin'.format(request_id, user))
            return True

    @method_wrapper
    def require_admin(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} checking if user {1} is admin'.format(request_id, user))
        resource = self.get(user, fields='admin')
        if not resource['admin']:
            self.log.debug('{0} user {1} is no admin'.format(request_id, user))
            raise PermError
        self.log.debug('{0} user {1} is admin'.format(request_id, user))

    @method_wrapper
    def search(self, _ids=None, admin=None, fields=None, sort=None, page=None, limit=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} executing user resource search'.format(request_id))
        query = {}
        self._filter_re(query, '_id', _ids)
        self._filter_boolean(query, 'admin', admin)
        result = []
        for item in self._coll.find(
            filter=query,
            projection=self._projection(fields)
        ).sort(self._sort(sort)).skip(self._pagination_skip(page, limit)).limit(self._pagination_limit(limit)):
            result.append(item)
        self.log.info('{0} success executing user resource search, found {1} items'.format(request_id, len(result)))
        return {'results': result}

    @method_wrapper
    def update(self, _id, delta):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} updating user resource {1}'.format(request_id, _id))
        if 'password' in delta:
            delta['password'] = self._password(delta['password'])
        update = {'$set': {}}
        for k, v in delta.items():
            update['$set'][k] = v
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} user resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success user resource {1}'.format(request_id, _id))
        return result
