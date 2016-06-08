# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from cerberus import errors
from eve.auth import BasicAuth, TokenAuth, HMACAuth
from hashlib import sha1
import hmac
from flask import request, make_response, redirect, url_for
from redis import Redis
from werkzeug.routing import BaseConverter
from uuid import UUID

redis = Redis()

class BearerAuth(BasicAuth):
    """ Overrides Eve's built-in basic authorization scheme and uses Redis to validate bearer token

    :param BasicAuth: Overriden Eve BasicAuth object
    """
    def check_auth(self, token, allowed_roles, resource, method):
        """ Check if API request is authorized.

        Examines token in header and checks Redis cache to see if token is valid. If so,
        request is allowed.
        :param token: OAuth 2.0 access token submitted.
        :param allowed_roles: Allowed user roles.
        :param resource: Resource being requested.
        :param method: HTTP method being executed (POST, GET, etc.)
        """
        import ipdb; ipdb.set_trace()  # XXX BREAKPOINT
        return redis.get(token)

    def authorized(self, allowed_roles, resource, method):
        """ Validates the the current request is allowed to pass through.

        :param allowed_roles: allowed roles for the current request, can be a
                              string or a list of roles.
        :param resource: resource being requested.
        """
        try:
            token = request.headers.get('Authorization').split(' ')[1]
        except:
            token = None
        return token and self.check_auth(token, allowed_roles, resource, method)



class UUIDValidator(Validator):
    """
    Extends the base mongo validator adding support for the uuid data-type
    """
    def _validate_type_uuid(self, field, value):
        try:
            UUID(value)
        except ValueError:
            self._error(field, "value '%s' cannot be converted to a UUID" %
                        value)



class UUIDConverter(BaseConverter):
    """
    UUID converter for the Werkzeug routing system.
    """

    def __init__(self, url_map):
        super(UUIDConverter, self).__init__(url_map)

    def to_python(self, value):
        return UUID(value)

    def to_url(self, value):
        return str(value)

# you can have multiple custom converters. Each converter has a key,
# which will be later used to designate endpoint urls, and a specialized
# BaseConverter subclass. In this case the url converter dictionary has
# only one item: our UUID converter.
url_converters = {'uuid': UUIDConverter}

from eve.io.base import BaseJSONEncoder


class UUIDEncoder(BaseJSONEncoder):
    """ JSONEconder subclass used by the json render function.
    This is different from BaseJSONEoncoder since it also addresses
    encoding of UUID
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        else:
            # delegate rendering to base class method (the base class
            # will properly render ObjectIds, datetimes, etc.)
            return super(UUIDEncoder, self).default(obj)



class HMACAuth(HMACAuth):
    def check_auth(self, userid, hmac_hash, headers, data, allowed_roles,
                   resource, method):
        # use Eve's own db driver; no additional connections/resources are
        # used
        self.set_request_auth_value(userid)
        return userid == 'root'
        #return True
        accounts = app.data.driver.db['accounts']
        user = accounts.find_one({'userid': userid})
        if user:
            secret_key = user['secret_key']
        # in this implementation we only hash request data, ignoring the
        # headers.
        return user and \
            hmac.new(str(secret_key), str(data), sha1).hexdigest() == \
                hmac_hash



class TAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        return token == 'token'



class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        # Check username and roles
        #accounts = app.data.driver.db['accounts']
        #lookup = {'username': 'nicola'}

        #if allowed_roles:
        #    lookup['roles'] = {'$in': allowed_roles}

        #account = accounts.find_one(lookup)
        self.set_request_auth_value(username)
        return True



class Validator(Validator):
    def _validate_empty(self, empty, field, value):
        super(Validator, self)._validate_empty(empty, field, value)
        if isinstance(value, list) and len(value) == 0 and not empty:
            self._error(field,errors.ERROR_EMPTY_NOT_ALLOWED)



def on_update(resoure, updates, original):
    updates['readonly'] = 'change!'

def post_GET_callback(r, req, l):
    print app.data.driver.db.activity.count()
    #app.post_internal('/ciao/contatti', {'firstname': 'Test', 'lastname': 'Name'})


def on_fetched_resource(resource, response):
    for doc in response['_items']:
        for field in doc.keys():
            if field.startswith('_'):
                del(doc[field])

def post_POST_projects(request, payload):
    print(request.get_json())
    print(payload.get_json())


app = Eve(auth=Auth)
#app.on_fetched_resource += on_fetched_resource
app.config['BANDWIDTH_SAVER'] = False

@app.route('/hello')
def hello():
    from eve.methods.get import get_internal
    r = get_internal('contacts')
    print r
    return "hello"

if __name__ == '__main__':
    #import logging
    #handler = logging.FileHandler('app.log')
    #handler.setFormatter(logging.Formatter(
    #    '%(asctime)s %(levelname)s: %(message)s '
    #    '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, url: %(url)s, method:%(method)s'))
    #app.logger.setLevel(logging.INFO)
    #app.logger.addHandler(handler)
    #app.on_pre_POST += pre_POST_callback
    app.run(debug=True)
