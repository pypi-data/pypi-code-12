from sqlalchemy.ext.declarative import declared_attr
from .base import db

class DeletedMixin(object):

    @declared_attr
    def deleted(self):
        return db.Column('deleted', db.Boolean, default=False, index=True, doc='是否删除')