from functools import wraps
import json

from libs.auth import Authenticate
from helpers.misc_hepler import get_bool_value


def check_if_authenticated(**details):
    def login_required(handler):
        @wraps(handler)
        def decorated_function(self, *args, **kwargs):
            auth_class = Authenticate()
            if self.auth_enabled:
                self.request.store_id = None
                if 'state' and 'permission' in details:
                    state = details['state']
                    permission = details['permission']
                else:
                    self.set_status(403)
                    self.write({'message': "unauthorized","success": False})
                    return

                # Retrieve session id from cookie.
                session_id = self.get_cookie('session')
                if session_id == None:
                    session_id = self.get_cookie(auth_class.session_id)

                if session_id is None:
                    self.set_status(403)
                    self.write({'message': "unauthorized","success": False})
                    return
                key = auth_class.session_prefix + session_id
                session_store = auth_class._alohomora_redis.hgetall(key)

                if not session_store:
                    self.set_status(403)
                    self.write({'message': "unauthorized","success": False})
                    return

                if 'is_superuser' not in session_store or not get_bool_value(session_store['is_superuser']):
                    if 'permission' in session_store:
                        allowed_permissions = json.loads(session_store['permission'])

                    if state not in allowed_permissions or permission not in allowed_permissions[state]:
                        self.set_status(403)
                        self.write({'message': "unauthorized","success": False})
                        return

                if auth_class.store_auth_required_key in details and details[auth_class.store_auth_required_key]:
                    self.request.store_id = None
                    if 'store_id' in session_store:
                        if not self.request.headers.get('store_id'):
                            self.request.store_id = session_store['store_id']

                self.request.user_id = None
                if 'user_id' in session_store:
                    if not self.request.headers.get('user_id'):
                        self.request.user_id = session_store['user_id']
                if 'username' in session_store:
                    if not self.request.headers.get('username'):
                        self.request.username = session_store['username']

                return handler(self, *args, **kwargs)
            else:
                return handler(self, *args, **kwargs)
        return decorated_function
    return login_required
