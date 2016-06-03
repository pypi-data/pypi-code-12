from datetime import datetime
from sqlalchemy import orm, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgres import UUID
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import uuid


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


class CRUDMixin(BaseMixin):
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

    @declared_attr
    def deleted(self):
        return db.Column('deleted', db.Boolean, default=False, index=True, doc='是否删除')

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


class DeletedMixin(object):

    @declared_attr
    def deleted(self):
        return db.Column('deleted', db.Boolean, default=False, index=True, doc='是否删除')


class EntryColumnMixin:
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


class EntryMixin:

    @property
    def entry_type(self):
        return self.__class__.__name__.lower()

    @property
    def entry_id(self):
        return self.id


class AccountMixin(object):

    @declared_attr
    def email(self):
        return db.Column('email', db.VARCHAR(255), index=True, unique=True, doc='用户邮箱,用来做登陆帐号')

    @declared_attr
    def password_hash(self):
        return db.Column('password_hash', db.VARCHAR(512), doc='用户密码的hash值')

    @declared_attr
    def email_confirmed(self):
        return db.Column('email_confirmed', db.Boolean, default=False, doc='邮箱是否经过确认')

    @property
    def password(self):
        raise ValueError('no password')

    @password.setter
    def password(self, password):
        setattr(self, 'password_hash', generate_password_hash(password))

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_token(cls, token, _=None):
        query = getattr(cls, 'query')
        data = cls.load_token(token)
        if data:
            return query.filter_by(id=uuid.UUID(data.get('user_id'))).first()

    @classmethod
    def get_by_account(cls, username, password):
        query = getattr(cls, 'query')
        user = query.filter_by(email=username).first()
        if user and user.verify_password(password):
            return user

    def generate_token(self, expiration=3600):
        """ 生成token"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user_id': self.id.hex})

    @classmethod
    def verify_token(cls, token):
        data = cls.load_token(token)
        return cls.query.filter_by(id=data.get('user_id'))

    @property
    def token(self):
        return self.generate_token(expiration=current_app.config.get('', 60 * 60 * 24 * 30))

    @staticmethod
    def load_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            return s.loads(token)
        except:
            return {}

    def confirm(self, token):
        data = self.load_token(token)

        if data and data.get('user_id') != self.id.hex:
            return False

        self.update(email_confirmed=True)
        return True
