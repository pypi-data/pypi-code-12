from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgres import UUID
from .base import (db)
from .crud import (CRUDMixin)


class EntryMixin:

    @property
    def entry_type(self):
        return self.__class__.__name__.lower()

    @property
    def entry_id(self):
        return self.id


class EntryColumnMixin(CRUDMixin):
    field = None

    @declared_attr
    def _entry_type(self):
        return db.Column('entry_type', db.String(255), index=True)

    @declared_attr
    def _entry_id(self):
        return db.Column('entry_id', UUID(as_uuid=True), index=True)

    @hybrid_property
    def entry_type(self):
        if self.has_property('entry_type'):
            return self._entry_type
        return self.__class__.__name__.lower()

    @entry_type.setter
    def entry_type(self, value):
        self._entry_type = value

    @entry_type.expression
    def entry_type(cls):
        return cls._entry_type

    @hybrid_property
    def entry_id(self):
        if self.has_property('entry_id'):
            return self._entry_id
        return self.id

    @entry_id.setter
    def entry_id(self, value):
        self._entry_id = value

    @entry_id.expression
    def entry_id(cls):
        return cls._entry_id

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


