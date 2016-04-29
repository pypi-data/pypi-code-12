from datetime import timedelta

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = ''

    APP_NAME = 'Bookbank'
    SECRET_KEY = 'add_secret'
    JWT_EXPIRATION_DELTA = timedelta(days=30)
    JWT_AUTH_URL_RULE = '/api/v1/auth'
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_HASH = 'sha512_crypt'
    SECURITY_PASSWORD_SALT = 'add_salt'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/db'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://127.0.0.1/bookbank'
    SQLALCHEMY_ECHO = True
    DEBUG = True


class TestingConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_DATABASE_URI = 'postgresql://127.0.0.1/bookbank'
    TESTING = True
