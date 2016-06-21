import json
import logging
import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    @classmethod
    def init_app(cls, app):
        """Send logs to stdout."""
        file_handler = logging.StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True


class UnitTestingConfig(Config):
    TESTING = True
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = True  # TODO: remove
    if os.getenv("VCAP_SERVICES"):
        services = json.loads(os.getenv("VCAP_SERVICES"))
        if "p-redis" in services:
            redis_env = services["p-redis"][0]["credentials"]
            REDIS_URL = "redis://:" + redis_env["password"] + "@" + redis_env["host"] + ":" + str(redis_env["port"]) + "/0"
        else:
            redis_env = services["rediscloud"][0]["credentials"]
            REDIS_URL = "redis://:" + redis_env["password"] + "@" + redis_env["hostname"] + ":" + str(redis_env["port"]) + "/0"


config = {
    "development": DevelopmentConfig,
    "unit_testing": UnitTestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
