
from flask import session, make_response, request
from flask_magic import Magic

from authomatic import Authomatic, provider_id
from authomatic.providers import oauth1, oauth2
from authomatic.adapters import WerkzeugAdapter

class OAuthomatic(object):
    oauth = None
    response = None

    def init_app(self, app):

        if app.config.get("MODULE_USER_ACCOUNT_ENABLE_OAUTH_LOGIN"):
            secret = app.config.get("SECRET_KEY")
            providers = app.config.get("MODULE_USER_ACCOUNT_OAUTH_PROVIDERS")
            config = {}
            auth_providers = []

            for provider, conf in providers.items():
                if hasattr(oauth2, provider):
                    cls = getattr(oauth2, provider)
                    conf["class_"] = conf["class_"] if "class_" in conf else cls
                elif hasattr(oauth1, provider):
                    cls = getattr(oauth1, provider)
                    conf["class_"] = conf["class_"] if "class_" in conf else cls
                else:
                    continue

                conf["id"] = provider_id()
                _provider = provider.lower()
                auth_providers.append(_provider)
                config[_provider] = conf

            self.oauth = Authomatic(
                config=config,
                secret=secret,
                session=session,
                report_errors=True
            )

            Magic.g(OAUTH_PROVIDERS=auth_providers)

    def login(self, provider):
        response = make_response()
        adapter = WerkzeugAdapter(request, response)
        login = self.oauth.login(adapter=adapter,
                                 provider_name=provider,
                                 session=session,
                                 session_saver=self._session_saver)
        self.response = response
        return login

    def _session_saver(self):
        session.modified = True

#oauth = OAuthomatic()
#Magic.bind(oauth.init_app)
