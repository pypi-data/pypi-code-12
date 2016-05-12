from functools import wraps
import json
import logging

from libs.auth import Authenticate
from helpers.misc_hepler import json_response

logger = logging.getLogger('auth_logger')


def check_if_authenticated(**details):
    def login_required(f):
        @wraps(f)
        def decorated_function(request, *args, **kwargs):
            auth_class = Authenticate()
            try:
                if auth_class.auth_enabled:
                    try:
                        auth_cookie = request.request.COOKIES[auth_class.session_id]
                    except KeyError:
                        return json_response({"message": "not logged in", "success": False}, status=401, cookie=None)
                    except AttributeError:
                        try:
                            auth_cookie = request.COOKIES[auth_class.session_id]
                        except KeyError:
                            return json_response({"message": "not logged in", "success": False}, status=401, cookie=None)

                    user_info = auth_class._alohomora_redis.hgetall(auth_class.session_prefix + auth_cookie)

                    if not user_info:
                        return json_response({"message": "not logged in", "success": False}, status=401, cookie=None)
                    if 'is_superuser' not in user_info or user_info['is_superuser'] != "True":
                        if 'state' and 'permission' in details:
                            allowed_state = details['state']
                            allowed_permissions = details['permission']

                            if not 'permission' in user_info:
                                return json_response({"message": "unauthorized", "success": False}, status=403)

                            actual_permissions = json.loads(user_info['permission'])
                            if allowed_state not in actual_permissions or allowed_permissions not in actual_permissions[
                                allowed_state]:
                                return json_response({"message": "unauthorized", "success": False}, status=403)

                            user_info['permission'] = actual_permissions
                            user_info['roles'] = json.loads(user_info['roles'])
                    user_info['is_superuser'] = True if user_info['is_superuser']=="True" else False
                    try:
                        request.request.user = user_info
                    except AttributeError:
                        request.user = user_info

                return f(request, *args, **kwargs)
            except Exception, e:
                logger.exception(e)
                import traceback;traceback.print_exc()
        return decorated_function

    return login_required
