from os import path

import sqlalchemy as _alchy
from sqlalchemy.ext.declarative import declarative_base as _declarative_base
import sqlalchemy.orm as _orm
from sqlalchemy import create_engine as _create_engine


_Base = _declarative_base()


class DatabaseManager:
    def __init__(self, database_filepath):
        engine = _create_engine('sqlite:///{}'.format(database_filepath))
        _Base.metadata.bind = engine
        DBSession = _orm.sessionmaker(bind=engine)
        self.session = DBSession()

    def record_message(self, service, author, text):
        A = Author
        try:
            author = self.session.query(A).filter(A.service == service,
                                                  A.name == author).one()

        except _orm.exc.NoResultFound:
            author = self._create_author(service, author)

        new_message = Message(text=text, author=author)
        self.session.add(new_message)
        self.session.commit()

    def _create_author(self, service, author):
        new_author = Author(name=author, service=service)
        self.session.add(new_author)
        self.session.commit()
        return new_author


class Author(_Base):
    __tablename__ = 'author'
    id = _alchy.Column(_alchy.Integer, primary_key=True)
    name = _alchy.Column(_alchy.String(50), nullable=False)
    service = _alchy.Column(_alchy.String(length=10))


class Message(_Base):
    __tablename__ = 'message'
    id = _alchy.Column(_alchy.Integer, primary_key=True)
    text = _alchy.Column(_alchy.String(length=500))
    author_id = _alchy.Column(_alchy.Integer, _alchy.ForeignKey('author.id'))
    author = _orm.relationship(Author)


def create_database(database_filepath):
    if not path.isfile(database_filepath):
        engine = _create_engine('sqlite:///{}'.format(database_filepath))
        _Base.metadata.create_all(engine)
