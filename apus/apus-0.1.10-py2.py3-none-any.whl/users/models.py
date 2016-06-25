from sqlalchemy import *
from sqlalchemy.orm import validates
from ..config.db import Base, session


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)

    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email

    def __repr__(self):
        return "Usuário: {}, E-mail: {}".format(self.username, self.email)

    @validates('email')
    def validate_email(self, key, users):
        assert '@' in users
        return users

    def save(self):
        session.add(self)
        session.commit()
        return self


