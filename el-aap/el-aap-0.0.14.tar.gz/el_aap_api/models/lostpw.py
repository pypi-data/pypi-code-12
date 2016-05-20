__author__ = 'schlitzer'

import datetime
import logging
import random
import string

from bottle import request
import pymongo.errors

from el_aap_api.models.mixins import FilterMixIn, ProjectionMixIn
from el_aap_api.errors import *


class LostPW(FilterMixIn, ProjectionMixIn):
    def __init__(self, coll):
        self.projection_fields = {
            '_id': 1,
        }
        self._coll = coll
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def _create_token(self):
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + '_-.') for _ in range(128))

    @method_wrapper
    def create(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} creating new lostpw token for user {1}'.format(request_id, user))
        token = self._create_token()
        lostpw = {
            'created': datetime.datetime.utcnow(),
            'token': token,
            '_id': user
        }
        try:
            self._coll.insert_one(lostpw)
        except pymongo.errors.DuplicateKeyError:
            self.log.warning('{0} there already is a recent lostpw token for user {1}'.format(request_id, user))
            raise LostPWErrorInProgress
        self.log.info('{0} success creating new lostpw token for user {1}'.format(request_id, user))
        return token

    @method_wrapper
    def delete(self, token):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} deleting lostpw token {1}'.format(request_id, token))
        self._coll.delete_one(filter={'token': token})
        self.log.info('{0} success deleting lostpw {1}'.format(request_id, token))

    @method_wrapper
    def get(self, token, fields=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} fetching user from lostpw token {1}'.format(request_id, token))
        result = self._coll.find_one(
            {
                'token': token
            },
            self._projection(fields)
        )
        if result is None:
            self.log.warning('{0} lostpw token {1} not found'.format(request_id, token))
            raise ResourceNotFound(token)
        self.log.info('{0} success fetching user from lostpw token {1}'.format(request_id, token))
        return result['_id']
