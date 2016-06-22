from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm


db = SQLAlchemy()


class BaseMixin(object):
    """ Base mixin
    """
    __table_args__ = {'extend_existing': True}

    @classmethod
    def column_properties(cls):
        properties = []
        mapper = getattr(cls, '__mapper__')

        if mapper and hasattr(mapper, 'iterate_properties'):
            properties = [p.key.lstrip('_') for p in mapper.iterate_properties if isinstance(p, (orm.ColumnProperty,))]

        return properties

    def as_dict(self, include=None, exclude=None):
        """
        :param include: 需要显示的属性列表
        :param exclude: 需要排除的属性列表
        :return:
        """
        fields = [field.strip('_') for field in self.column_properties()]

        exportable_fields = (include or []) + fields
        exportable_fields = set(exportable_fields) - set(exclude or [])

        result = dict()
        for field in exportable_fields:
            value = getattr(self, field)
            if hasattr(value, '__call__'):
                value = value()
            result[field] = value

        return result

    @classmethod
    def has_property(cls, name):
        return name in cls.column_properties()