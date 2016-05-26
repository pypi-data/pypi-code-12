import peewee
from playhouse import db_url
from woodstove import conf, exceptions


DB_URI = conf.get('woodstove', 'db_uri', 'sqlite:///:memory:')
__db__ = db_url.connect(DB_URI)


class BaseModel(peewee.Model):
    class Meta:
        database = __db__


def get_db(auto_connect=True):
    if auto_connect and __db__.is_closed():
        __db__.connect()

    return __db__


def get_obj(model, key):
    r = model.select().where(model._meta.primary_key == key)
    try:
        return r.get()
    except peewee.DoesNotExist:
        raise exceptions.NotFoundException
