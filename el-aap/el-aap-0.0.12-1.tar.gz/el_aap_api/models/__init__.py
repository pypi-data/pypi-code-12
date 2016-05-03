__author__ = 'schlitzer'

import inspect

from bottle import PluginError

from el_aap_api.errors import ValidationError
from el_aap_api.models.aa import AuthenticationAuthorization
from el_aap_api.models.lostpw import LostPW
from el_aap_api.models.permissions import Permissions
from el_aap_api.models.roles import Roles
from el_aap_api.models.session import Sessions
from el_aap_api.models.users import Users


__all__ = [
    'ValidationError',
    'MetaPlugin',
    'AuthenticationAuthorization',
    'LostPW',
    'Permissions',
    'Roles',
    'Sessions',
    'Users',
]


class MetaPlugin(object):
    api = 2

    def __init__(self, model, keyword):
        self.keyword = keyword
        self.model = model

    def setup(self, app):
        for other in app.plugins:
            if not isinstance(other, MetaPlugin):
                continue
            if other.keyword == self.keyword:
                raise PluginError('Found another plugin with the same keyword: {0}'.format(self.keyword))

    def apply(self, callback, context):
        callback_args = inspect.getargspec(context.callback)[0]
        if self.keyword not in callback_args:
            return callback

        def wrapper(*args, **kwargs):
            kwargs[self.keyword] = self.model
            rv = callback(*args, **kwargs)
            return rv
        return wrapper
