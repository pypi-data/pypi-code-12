__author__ = 'schlitzer'

import logging

from bottle import request
import pymongo
import pymongo.errors

from el_aap_api.models.mixins import FilterMixIn, PaginationSkipMixIn, ProjectionMixIn, SortMixIn
from el_aap_api.errors import *


class Roles(FilterMixIn, PaginationSkipMixIn, ProjectionMixIn, SortMixIn):
    def __init__(self, coll):
        self.projection_fields = {
            '_id': 1,
            'description': 1,
            'users': 1
        }
        self.sort_fields = [
            ('_id', pymongo.ASCENDING)
        ]
        self._coll = coll
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def add_users(self, _id, users):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} add users {1} to role resource {2}'.format(request_id, users, _id))
        update = {'$addToSet': {"users": {"$each": users}}}
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} role resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating role resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def check_ids(self, _ids):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} checking if role ids {1} exist'.format(request_id, _ids))
        count = self._coll.find(
                filter={'_id': {'$in': _ids}},
                projection={'id': 1}).count()
        return len(_ids) == count

    @method_wrapper
    def create(self, role):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} creating new role resource {1}'.format(request_id, role['_id']))
        try:
            self._coll.insert_one(role)
        except pymongo.errors.DuplicateKeyError:
            self.log.warning('{0} role resource {1} already exists'.format(request_id, role['_id']))
            raise DuplicateResource(role['_id'])
        self.log.info('{0} success creating new role resource {1}'.format(request_id, role['_id']))
        return self.get(role['_id'])

    @method_wrapper
    def delete(self, _id):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} deleting role resource {1}'.format(request_id, _id))
        result = self._coll.delete_one(filter={'_id': _id})
        if result.deleted_count is 0:
            self.log.warning('{0} role resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success deleting role resource {1}'.format(request_id, _id))
        return

    @method_wrapper
    def get(self, _id, fields=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} fetching role resource {1}'.format(request_id, _id))
        result = self._coll.find_one(
                filter={'_id': _id},
                projection=self._projection(fields)
        )
        if result is None:
            self.log.warning('{0} role resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success fetching role resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def remove_users(self, _id, users):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} remove users {1} to role resource {2}'.format(request_id, users, _id))
        update = {"$pullAll": {"users": users}}
        result = self._coll.find_one_and_update(
            filter={'_id': _id},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            self.log.warning('{0} role resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating role resource {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def remove_user_from_all(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} removing user {1} from all role resources'.format(request_id, user))
        self._coll.update_many(
            filter={"users": user},
            update={"$pull": {"users": user}}
        )
        self.log.debug('{0} success removing user {1} from all role resources'.format(request_id, user))

    @method_wrapper
    def search(self, _ids=None, users=None, fields=None, sort=None, page=None, limit=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} executing role resource search'.format(request_id))
        query = {}
        self._filter_re(query, '_id', _ids)
        self._filter_list(query, 'users', users)
        result = []
        for item in self._coll.find(
                filter=query,
                projection=self._projection(fields)
        ).sort(self._sort(sort)).skip(self._pagination_skip(page, limit)).limit(self._pagination_limit(limit)):
            result.append(item)
        self.log.info('{0} success executing role resource search, found {1} items'.format(request_id, len(result)))
        return {'results': result}

    @method_wrapper
    def update(self, _id, delta):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} updating role resource {1}'.format(request_id, _id))
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
            self.log.warning('{0} role resource {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success updating role resource {1}'.format(request_id, _id))
        return result
