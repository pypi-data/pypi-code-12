__author__ = 'schlitzer'

import logging

from bottle import request
import pymongo
import pymongo.errors

from el_aap_api.models.mixins import FilterMixIn, PaginationSkipMixIn, ProjectionMixIn, SortMixIn
from el_aap_api.errors import *


class Permissions(FilterMixIn, PaginationSkipMixIn, ProjectionMixIn, SortMixIn):
    def __init__(self, coll):
        self.projection_fields = {
            '_id': 1,
            'description': 1,
            'permissions': 1,
            'roles': 1,
            'scope': 1
        }
        self.sort_fields = [
            ('_id', pymongo.ASCENDING),
            ('scope', pymongo.ASCENDING)
        ]
        self._coll = coll
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def add_permissions(self, _id, permissions):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} add permissions {1} to permission resource {2}'.format(request_id, permissions, _id))
        update = {'$addToSet': {'permissions': {'$each': permissions}}}
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating permission resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def add_roles(self, _id, roles):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} add roles {1} to permission resource {2}'.format(request_id, roles, _id))
        update = {'$addToSet': {'roles': {'$each': roles}}}
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating permission resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def create(self, permission):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} creating new permission resource {1}'.format(request_id, permission['_id']))
        try:
            self._coll.insert_one(permission)
        except pymongo.errors.DuplicateKeyError:
            self.log.warning('{0} permission resource {1} already exists'.format(request_id, permission['_id']))
            raise DuplicateResource(permission['_id'])
        self.log.info('{0} success creating permission resource {1}'.format(request_id, permission['_id']))
        return self.get(permission['_id'])

    @method_wrapper
    def delete(self, _id):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} deleting permission resource {1}'.format(request_id, _id))
        result = self._coll.delete_one(filter={'_id': _id})
        if result.deleted_count is 0:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success deleting permission resource {1}'.format(request_id, _id))
        return

    @method_wrapper
    def get(self, _id, fields=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} fetching permission resource {1}'.format(request_id, _id))
        result = self._coll.find_one(
            filter={'_id': _id},
            projection=self._projection(fields)
        )
        if result is None:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        result['_id'] = _id
        self.log.info('{0} success fetching permission resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def remove_permissions(self, _id, permissions):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} remove permissions {1} from permission resource {2}'.format(request_id, permissions, _id))
        update = {'$pullAll': {'permissions': permissions}}
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating permission resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def remove_roles(self, _id, roles):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} remove roles {1} from permission resource {2}'.format(request_id, roles, _id))
        update = {'$pullAll': {'roles': roles}}
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating permission resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def remove_role_from_all(self, role):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} removing role {1} from all permission resources'.format(request_id, role))
        self._coll.update_many(
            filter={'roles': role},
            update={'$pull': {'roles': role}}
        )
        self.log.debug('{0} success removing role {1} from all permission resources'.format(request_id, role))

    @method_wrapper
    def search(self, _ids=None, scope=None, permissions=None, roles=None, fields=None, sort=None, page=None, limit=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} executing permission resource search'.format(request_id))
        query = {}
        self._filter_re(query, '_id', _ids)
        self._filter_list(query, 'permissions', permissions)
        self._filter_list(query, 'scope', scope)
        self._filter_list(query, 'roles', roles)
        result = []
        for item in self._coll.find(
                filter=query,
                projection=self._projection(fields)
        ).sort(self._sort(sort)).skip(self._pagination_skip(page, limit)).limit(self._pagination_limit(limit)):
            result.append(item)
        self.log.info('{0} success executing permission resource search, found {1} items'.format(request_id, len(result)))
        return {'results': result}

    @method_wrapper
    def update(self, _id, delta):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} updating permission resource {1}'.format(request_id, _id))
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update={'$set': delta},
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} permission resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        result['_id'] = _id
        self.log.info('{0} success updating permission resource {1}'.format(request_id, _id))
        return result
