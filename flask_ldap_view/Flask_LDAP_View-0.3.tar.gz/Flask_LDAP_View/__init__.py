import ldap
from functools import wraps
from flask import current_app, redirect , g
import re


__all__ = ['LDAP_VIEW']


class LDAP_VIEW(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    @staticmethod
    def error(e):
        e = e[0]
        if 'desc' in e:
            return e['desc']
        else:
            return str(e)

    @staticmethod
    def search_memberof(records, username):
        """finds the memeberof field by username at login and returns the group list from record"""
        count = 0
        for x in records:
            if x[1]['objectClass'][1] == 'person':
                if x[1]['sAMAccountName'][0] == username:
                    memberof = records[count][1]['memberOf']
                    memberof_clean = [(re.sub(r'CN=|,OU.*', '',x)) for x in memberof]
                    return memberof_clean
            count = count + 1
        raise ValueError('User does not have any groups, please contact your Active Directory admin')

    @staticmethod
    def search_DN_name(records, username):
        "Returns distinguishedName from record that matches the username at login"
        count = 0
        for x in records:
            if x[1]['objectClass'][1] == 'person':
                if x[1]['sAMAccountName'][0] == username:
                    return records[count][1]['distinguishedName'][0]
            count = count + 1
        raise ValueError('User does not exist, please contact your Active Directory admin')

    @property
    def initialize(self):
        """Initialize a connection to the LDAP server.

        :return: LDAP connection object.
        """

        conn = ldap.initialize(current_app.config['LDAP_HOST'])
        conn.protocol_version = ldap.VERSION3
        return conn

    @property
    def bind(self):
        """Attempts to bind to the LDAP server using the credentials of the
        service account.

        :return: Bound LDAP connection object if successful or ``None`` if
            unsuccessful.
        """

        conn = self.initialize
        conn.simple_bind_s(
            current_app.config['LDAP_USERNAME'],
            current_app.config['LDAP_PASSWORD'])
        return conn

    def get_object_details(self,username):
        """Gathers distinguished name for the user and the groups the user is part of"""

        conn = self.bind
        records = conn.search_s(current_app.config['LDAP_BASE_DN'],ldap.SCOPE_SUBTREE)
        user_dn = self.search_DN_name(records, username)
        user_memberof = self.search_memberof(records, username)
        return user_dn, user_memberof

    def bind_user(self, username, password):
        """Attempts to bind the user credentials that were supplied at login screen"""

        try:
            user_dn, user_memberof = self.get_object_details(username)
            conn = self.initialize
            conn.simple_bind_s(user_dn, password)
            return user_memberof
        except Exception, e:
            return ValueError(self.error(e))

    def group_required(self,groups=None):
        """Views determines if the user is part of LDAP group. If not they will be redirected"""


        def wrapper(func):
            @wraps(func)
            def _wrapper(*args, **kwargs):
                try:
                    for group in groups:
                        if group in g.user_memberof:
                            return func(*args, **kwargs)
                    return redirect(current_app.config['LDAP_UNAUTHORIZED_REDIRECT'])
                except:
                    return redirect(current_app.config['LDAP_UNAUTHORIZED_REDIRECT'])
            return _wrapper
        return wrapper





