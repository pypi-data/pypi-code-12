from __future__ import absolute_import
from pyramid.config import Configurator

from sqlalchemy import engine_from_config
from sqlalchemy_utils import force_auto_coercion, force_instant_defaults

from unicore.webhooks.models import DBSession, Base

# See: http://sqlalchemy-utils.readthedocs.org/en/latest/listeners.html
force_auto_coercion()
force_instant_defaults()


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('unicore.webhooks')
    return config.make_wsgi_app()


def includeme(config):
    config.include('cornice')
    config.scan()
    settings = config.registry.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
