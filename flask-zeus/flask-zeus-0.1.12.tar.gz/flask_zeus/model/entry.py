from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgres import UUID
from flask_login import current_user
from .base import (db)
from .crud import (CRUDMixin)


class MarshalLabelMixin:

    def __marshallable__(self):
        data = self.__dict__
        data.update({
            'entry_type': self.cls_entry_type(),
            'entry_id': self.id
        })
        return data

    @classmethod
    def cls_entry_type(cls):
        return cls.__name__.lower()


class EntryMixin(CRUDMixin):
    # 属性名称
    # 例子: is_followed, is_praised
    attribute = None

    @declared_attr
    def entry_type(self):
        return db.Column('entry_type', db.String(255), index=True)

    @declared_attr
    def entry_id(self):
        return db.Column('entry_id', UUID(as_uuid=True), index=True)

    @classmethod
    def for_entries(cls, items, attribute=None, child=None):
        attribute = attribute or cls.attribute

        if not attribute:
            raise AttributeError('需要设置field值')

        data = items

        if child:
            data = [getattr(item, child) for item in items]

        data_id = set([item.id for item in data])
        results = dict((item_id, False) for item_id in data_id)

        if current_user.is_authenticated:
            query = getattr(cls, 'query')

            res = query\
                .filter(cls.entry_id.in_(data_id))\
                .filter_by(user_id=current_user.id)\
                .all()

            for item in res:
                results[item.entry_id] = True

        for item in data:
            setattr(item, attribute, results.get(item.id))

        return items


