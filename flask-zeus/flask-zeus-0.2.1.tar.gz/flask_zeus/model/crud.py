from sqlalchemy import text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgres import UUID
from datetime import datetime
from .base import (db, BaseMixin)
from .delete import DeletedMixin
from ..decorators import classproperty
import re


class CRUDMixin(BaseMixin, DeletedMixin):
    """ Basic CRUD mixin
    """

    @declared_attr
    def id(self):
        return db.Column('id', UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), primary_key=True, doc='主键')

    @declared_attr
    def created_at(self):
        return db.Column('created_at', db.DateTime, default=datetime.now, index=True, nullable=False, doc='创建时间')

    @declared_attr
    def updated_at(self):
        return db.Column('updated_at', db.DateTime, default=datetime.now, index=True, nullable=False, doc='更新时间')

    @classmethod
    def get(cls, row_id):
        query = getattr(cls, 'query')
        return query.get(row_id)

    @classmethod
    def create(cls, commit=True, **kwargs):
        return cls(**kwargs).save(commit)

    def save(self, commit=True):
        db.session.add(self)

        if commit:
            db.session.commit()

        return self

    def delete(self, commit=True):
        if self.has_property('deleted'):
            setattr(self, 'deleted', True)
            db.session.add(self)
        else:
            db.session.delete(self)

        if commit:
            db.session.commit()

    def update(self, commit=True, **kwargs):
        return self._set_attributes(**kwargs).save(commit)

    def _set_attributes(self, **kwargs):
        for k, v in kwargs.items():

            if k.startswith('_'):
                raise ValueError('私有属性不允许被设置')

            if self.has_property(k):
                setattr(self, k, v)

        return self

    def increase(self, field, step=1):
        self.update(**{field: getattr(self, field) + step})

    def __marshallable__(self):
        data = self.__dict__
        data.update({
            'item_type': getattr(self, 'item_type'),
            'item_id': getattr(self, 'id')
        })
        return data

    @classproperty
    def item_type(cls):
        regex = re.compile(r'([A-Z])+')
        return regex.sub(lambda x: '/{}'.format(x.group(0).lower()), cls.__name__).strip('/')

