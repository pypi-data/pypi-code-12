from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates

from apus.config.db import Base, create_table


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)

    def __repr__(self):
        return "Usuário: {}, E-mail: {}".format(self.username, self.email)

    @validates('email')
    def validate_email(self, key, users):
        assert '@' in users
        return users


create_table()
