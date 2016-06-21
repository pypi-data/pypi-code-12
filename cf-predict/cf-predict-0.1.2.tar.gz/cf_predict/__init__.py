import sys
import os
from flask import Flask
from mockredis import MockRedis
from flask_redis import FlaskRedis
from .config import config

from .api import api_bp

__project__ = 'cf-predict'
__version__ = '0.1.2'

VERSION = "{0} v{1}".format(__project__, __version__)

PYTHON_VERSION = 3, 4

if sys.version_info < PYTHON_VERSION:  # pragma: no cover (manual test)
    sys.exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))


class MockRedisWrapper(MockRedis):
    """A wrapper to add the `from_url` classmethod."""

    @classmethod
    def from_url(cls, *args, **kwargs):
        return cls()


def create_app(config_name):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    if app.testing:
        redis_store = FlaskRedis.from_custom_provider(MockRedisWrapper)
    else:
        redis_store = FlaskRedis()
    redis_store.init_app(app)
    app.register_blueprint(api_bp)
    return app


if __name__ == '__main__':  # pragma: no cover
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(host=app.config['HOST'], port=app.config['PORT'])
