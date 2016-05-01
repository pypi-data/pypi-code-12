"""
APM is app performance monitoring service.
Currently uses NewRelic, to monitor the app

How to use

from magic_xxl.flask import newrelic_apm as apm

apm.apm.set_name("www")

Requirements:
    config:
        APPLICATION_NAME
        NEWRELIC_LICENSE_KEY
"""

from flask_magic import init_app, get_env
import newrelic.agent

newrelic.agent.initialize()
settings = newrelic.agent.global_settings()

class NewRelicAPM(object):
    _app = None
    _app_name = "www"

    def init_app(self, app):

        wp_application_name = app.config.get("APPLICATION_NAME")
        env_name = get_env().lower()
        app_name = "%s/%s:%s" % (wp_application_name, self._app_name, env_name)

        settings.app_name = app_name
        settings.license_key = app.config.get("NEWRELIC_LICENSE_KEY")

    def set_name(self, app_name):
        self._app_name = app_name

apm = NewRelicAPM()
init_app(apm.init_app)
