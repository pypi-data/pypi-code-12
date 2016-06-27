# -*- encoding: utf-8 -*-

from xbus.broker.cli import get_config
from xbus.broker.model import setup_app

__author__ = 'faide'


def setup_xbusbroker():  # pragma: nocover
    """ a simple cmd line that will create a default db
    """
    # just run the setup script by passing it a config instance
    setup_app(get_config())
