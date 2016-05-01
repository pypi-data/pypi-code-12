from prosodypy.base import ProsodyBasePlugin

class ProsodyAuthPlugin(ProsodyBasePlugin):
    """
    Base class for authentication plugins.
    """

    def __init__(self, *args):
        super(ProsodyAuthPlugin, self).__init__(*args)
        self.sasl = self.lua.require('util.sasl')
        provider = {k:getattr(self, k) for k in dir(self)}
        self.module.provides('auth', self.lua.table_from(provider))

    def test_password(self, username, password):
        raise NotImplementedError("Should be implemented in derived class.")

    def get_password(self, username):
        raise NotImplementedError("Should be implemented in derived class.")

    def set_password(self, username, password):
        raise NotImplementedError("Should be implemented in derived class.")

    def user_exists(self, username):
        raise NotImplementedError("Should be implemented in derived class.")

    def create_user(self, username, password):
        raise NotImplementedError("Should be implemented in derived class.")

    def get_sasl_handler(self, session):
        raise NotImplementedError("Should be implemented in derived class.")

    def users(self):
        raise NotImplementedError("Should be implemented in derived class.")
