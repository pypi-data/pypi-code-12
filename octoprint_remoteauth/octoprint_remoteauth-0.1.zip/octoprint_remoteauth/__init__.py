# -*- coding: utf-8 -*-
from octoprint.users import UserManager, DummyUser
from octoprint.settings import settings
import urllib
import urllib2
from urllib2 import URLError


class RemoteAuthUserManager(UserManager):
    # TODO: implement user settings?

    def __init__(self):
        UserManager.__init__(self)
        self._customized = True
        self._check_password_url = settings().get(["accessControl", "remoteAuthCheckPasswordUrl"])
        # user cache dictionnary
        self._users = {}

    def checkPassword(self, username, password):
        # validate password in api
        values = {
            "username": username,
            "password": password
        }
        data = urllib.urlencode(values)
        if self._check_password_url is None:
            raise Exception("Config Entry: accessControl.remoteAuthCheckPasswordUrl has to be defined.")
        req = urllib2.Request(self._check_password_url, data)
        try:
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                return True
        except URLError:
            pass
        return False

    def findUser(self, userid=None, apikey=None, session=None):
        user = UserManager.findUser(self, userid=userid, session=session)
        if user is not None:
            return user

        if userid in self._users:
            return self._users[userid]

        # get user from api
        user = DummyUser()
        user._username = userid
        # TODO: lookup user and add correct roles
        user._roles = ["user", "admin"]
        self._users[userid] = user

        # return user to continue to checkPassword
        return user

    def getAllUsers(self):
        return map(lambda x: x.asDict(), self._users.values())
