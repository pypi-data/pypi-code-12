__author__ = 'schlitzer'

import logging

from bottle import request

from el_aap_api.errors import *


class AuthenticationAuthorization(object):
    def __init__(self, users, sessions):
        self.users = users
        self.sessions = sessions
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def _get_session_from_header(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} trying to get session from header'.format(request_id))
        result = {}
        _id = request.get_header('X-SID', False)
        token = request.get_header('X-TOKEN', False)
        if _id and token:
            result['_id'] = _id
            result['token'] = token
            self.log.debug('{0} success trying to get session from header'.format(request_id))
            return result
        self.log.debug('{0} failed trying to get session from header'.format(request_id))

    @method_wrapper
    def _get_session_from_cookie(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} trying to get session from cookie'.format(request_id))
        result = {}
        _id = request.get_cookie('sid', False)
        token = request.get_cookie('token', False)
        if _id and token:
            result['_id'] = _id
            result['token'] = token
            self.log.debug('{0} success trying to get session from cookie'.format(request_id))
            return result
        self.log.debug('{0} failed trying to get session from cookie'.format(request_id))

    @method_wrapper
    def _get_session(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} trying to get session'.format(request_id))
        session = self._get_session_from_header()
        if not session:
            session = self._get_session_from_cookie()
        if not session:
            self.log.warning('{0} failed trying to get session'.format(request_id))
            raise SessionError
        self.log.debug('{0} success trying to get session'.format(request_id))
        return session

    @method_wrapper
    def get_session(self):
        session = self._get_session()
        self.sessions.check_session(session)
        return session

    @method_wrapper
    def get_user(self):
        return self.sessions.check_session(self._get_session())

    @method_wrapper
    def require_admin(self):
        self.users.require_admin(self.get_user())
