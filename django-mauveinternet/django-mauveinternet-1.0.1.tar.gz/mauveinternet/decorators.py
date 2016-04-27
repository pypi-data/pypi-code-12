import re
import base64
import datetime

from django.http import HttpResponse

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class HttpAuthentication(object):
    def __init__(self, view, realm='Django', log=None):
        self.view = view
        self.realm=realm
        self.log = log

    def write_log(self, msg):
        if not self.log:
            return

        f = open(self.log, 'a')
        f.write('[%s] %s'%(datetime.datetime.now(), msg))
        f.close()

    def not_authorized(self):
        response = HttpResponse('<h1>401 Not Authorized</h1>', status=401)
        response['WWW-Authenticate']='Basic realm="%s"'%self.realm
        return response

    def authenticate(self, request):
        """Performs HTTP authentication on request.

        If the user can be authenticated from the request headers,
        request.user updated to show the authenticated user."""

        for k in ['HTTP_AUTHORIZATION', 'Authorization']:
            if k in request.META:
                auth = request.META[k]
                break
        else:
            self.write_log('No credentials received')
            return

        mo = re.match(r'Basic (.*)', auth)
        if not mo:
            self.write_log('Invalid authentication mechanism')
            return
        auth = base64.decodestring(mo.group(1))
        try:
            username, password = auth.split(':', 1)
        except ValueError:
            self.write_log("Couldn't parse credentials")
            return

        user = authenticate(username=username, password=password)
        if user:
            self.write_log("User %s authenticated" % user)
            request.user = user
        self.write_log("Login attempt for %s denied" % username)

    def __call__(self, request, *args, **kwargs):
        """Attempts to authenticate a user using HTTP basic authentication.

        If the user is not authenticated by this or the standard Django scheme,
        serves a plain HTTP 401 page.
        """
        self.authenticate(request)
        if not request.user.is_authenticated():
            return self.not_authorized()

        return self.__dict__['view'](request, *args, **kwargs)


def http_authentication(realm, log=None):
    def authenticated_view(view):
        return HttpAuthentication(view, realm, log)
    return authenticated_view


def not_cacheable(view):
    def _force_no_caching(*args, **kwargs):
        response = view(*args, **kwargs)
        response['Pragma'] = 'no-cache'
        response['Cache-Control'] = 'no-cache, no-store'
        return response

    from django.utils.functional import update_wrapper
    return update_wrapper(_force_no_caching, view)
