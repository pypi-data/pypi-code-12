from prosodypy.auth import ProsodyAuthPlugin

class ProsodyPlugin(ProsodyAuthPlugin):
    """
    A rewrite of mod_auth_anonymous.lua in Python for an example of how to
    write auth plugins in Python.
    """
    name = 'pyanonymous'

    def __init__(self, *args):
        super(ProsodyPlugin, self).__init__(*args)
        self.datamanager = self.lua.require('util.datamanager')

    def test_password(self, username, password):
        raise NotImplementedError("Password based auth not supported.")

    def get_password(self, username):
        raise NotImplementedError("Password not available.")

    def set_password(self, username, password):
        raise NotImplementedError("Password based auth not supported.")

    def user_exists(self, username):
        # FIXME check if anonymous user is connected?
        raise NotImplementedError("Only anonymous users are supported.")

    def create_user(self, username, password):
        raise NotImplementedError("Account creation/modification not supported.")

    def get_sasl_handler(self, session):
        anonymous_authentication_profile = self.lua.table_from({
            'anonymous': lambda sasl, username, realm: True,
        })
        return self.sasl.new(
            self.module.host,
            anonymous_authentication_profile,
        )

    def users(self):
        return (
            self.lua.eval('next'),
            self.prosody.hosts[self.module.host].sessions,
            None,
        )

    def dm_callback(self, username, host, datastore, data):
        if host == self.module.host:
            return False
        return username, host, datastore, data

    def load(self):
        if not self.module.get_option_boolean("allow_anonymous_s2s", False):
            self.module.hook("route/remote", lambda event: False, 300)
        self.datamanager.add_callback(self.dm_callback)

    def unload(self):
        self.datamanager.remove_callback(self.dm_callback)

