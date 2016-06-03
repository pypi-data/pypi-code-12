from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgres import UUID
from flask_login import current_user
from .base import (db)
from .crud import (CRUDMixin)


class MarshalLabelMixin:

    def __marshallable__(self):
        data = self.__dict__
        data.update({
            'entry_type': self.__class__.__name__.lower(),
            'entry_id': self.id
        })
        return data


class EntryMixin(CRUDMixin):
    field = None

    @declared_attr
    def entry_type(self):
        return db.Column('entry_type', db.String(255), index=True)

    @declared_attr
    def entry_id(self):
        return db.Column('entry_id', UUID(as_uuid=True), index=True)

    @classmethod
    def for_entries(cls, items, field=None, child=None):
        field = field or cls.field

        if not field:
            raise AttributeError('需要设置field值')

        data = items
        if child:
            data = [getattr(item, child) for item in items]

        data_id = set([item.id for item in data])
        results = dict((item_id, False) for item_id in data_id)

        if current_user.is_authenticated:
            res = cls.query \
                .filter(cls.entry_id.in_(data_id)) \
                .filter_by(user_id=current_user.id) \
                .all()
            for item in res:
                results[item.entry_id] = True

        if field:
            for item in data:
                setattr(item, field, results.get(item.id))

        return items


