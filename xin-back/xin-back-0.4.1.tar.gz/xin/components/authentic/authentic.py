from autobahn.wamp.exception import ApplicationError
from autobahn.twisted.wamp import ApplicationSession, Application
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.internet.defer import inlineCallbacks, returnValue
from datetime import datetime

from .config import LISTEN_PORT, RETRIEVE_USER_RPC
from .rest import rest_api_factory
from .tools import decode_token


class AuthenticSession(ApplicationSession):

    def onJoin(self, details):

        rest_app = rest_api_factory(self)
        reactor.listenTCP(LISTEN_PORT, Site(rest_app.resource()))

        @inlineCallbacks
        def authenticate(realm, login, details):
            token = decode_token(details['ticket'])
            if (not token or login != token['login'] or
                    token['exp'] < datetime.utcnow().timestamp()):
                raise ApplicationError("xin.authentic.invalid_ticket",
                    "could not authenticate session - invalid token"
                    " '{}' for user {}".format(token, login))
                raise ApplicationError('Invalid token')
            user = yield self.call(RETRIEVE_USER_RPC, login)
            if not user:
                raise ApplicationError("xin.authentic.no_such_user",
                    "could not authenticate session - no such user {}".format(login))
                raise ApplicationError('Unknown user')
            print("[AUTHENTIC] WAMP-Ticket dynamic authenticator invoked: realm='{}', "
                  "authid='{}', ticket='{}'".format(realm, login, details))
            returnValue(user.get('role'))

        return self.register(authenticate, 'xin.authentic.authenticate')


if __name__ == "__main__":
    import sys
    from twisted.python import log
    log.startLogging(sys.stdout)

    wampapp = Application()
    wampapp.run("ws://localhost:8080", "realm1", standalone=False)
