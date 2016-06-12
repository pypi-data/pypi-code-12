from sqlalchemy.ext.declarative import declared_attr
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from .base import db
from .crud import CRUDMixin
from uuid import UUID


class AccountMixin(CRUDMixin):

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
            return query.filter_by(id=UUID(data.get('user_id'))).first()

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
