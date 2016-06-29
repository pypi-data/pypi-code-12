# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet


class DatabaseAsAServiceApi(object):
    def __init__(self, databaseinfra, credentials):
        self.databaseinfra = databaseinfra
        self.credentials = credentials

    @property
    def user(self):
        return self.credentials.user

    @property
    def password(self):
        return self.credentials.password

    @property
    def endpoint(self):
        return self.credentials.endpoint

    @property
    def key(self):
        return self.credentials.secret

    @property
    def cipher(self):
        return Fernet(self.key)

    @property
    def port(self):
        return self.credentials.get_parameter_by_name('port')

    @property
    def database_name(self):
        return self.credentials.get_parameter_by_name('database_name')
