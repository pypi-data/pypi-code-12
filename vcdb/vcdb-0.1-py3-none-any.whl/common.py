"""
Common classes and functions for vcdb.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.
import os
import shutil

import sqlalchemy
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


class VcdbError(Exception):
    pass


def func_name():
    import traceback
    return traceback.extract_stack(None, 2)[0][2]


def ensure_is_removed(path):
    try:
        shutil.rmtree(path)
    except NotADirectoryError:
        os.remove(path)
    except FileNotFoundError:
        if os.path.exists(path):
            raise


def ensure_folder_is_empty(empty_path):
    ensure_is_removed(empty_path)
    os.makedirs(empty_path, exist_ok=True)


#: Maximum number of characters to represent an author.
AUTHOR_LENGTH = 16

MAX_REPOSITORY_ID_DIGITS = 2

#: Maximum number of characters to represent a Change.commit_id.
COMMIT_ID_LENGTH = 16  # NOTE: The Linux Kernel currently uses 12 characters for git hashes.

#: Maximum number of characters to represent a Change.change_id.
CHANGE_ID_LENGTH = 1 + MAX_REPOSITORY_ID_DIGITS + COMMIT_ID_LENGTH

#: Maximum number of characters to store in Change.commit_message.
COMMIT_MESSAGE_LENGTH = 1020

#: Maximum number of characters to represent a URI or a path in the repository.
PATH_LENGTH = 512

DeclarativeBase = declarative_base()


def change_id_for(repository_id, commit_id):
    assert 0 < repository_id < 10 ** MAX_REPOSITORY_ID_DIGITS
    assert repository_id is not None

    result = '%0*d-%s' % (MAX_REPOSITORY_ID_DIGITS, repository_id, commit_id)
    assert len(result) <= CHANGE_ID_LENGTH, 'result=%r' % result
    return result


class Repository(DeclarativeBase):
    __tablename__ = 'repositories'
    repository_id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    uri = Column(String(PATH_LENGTH), nullable=False)
    last_change_id = Column(String(CHANGE_ID_LENGTH))  # NOTE: Not a ForeignKey to avoid circular dependency.

    UniqueConstraint('uri')

    def __repr__(self):
        return '<Repository(repository_id=%r, uri=%r, last_synctime=%r)>' % (
            self.repository_id, self.uri, self.last_synctime
        )


class Change(DeclarativeBase):
    """
    A change that has been taken place in a certain repository.
    """
    __tablename__ = 'changes'
    author = Column(String(AUTHOR_LENGTH))
    change_id = Column(String(CHANGE_ID_LENGTH), nullable=False, primary_key=True)
    commit_id = Column(String(COMMIT_ID_LENGTH), nullable=False)
    commit_message = Column(String(COMMIT_MESSAGE_LENGTH))
    commit_time = Column(DateTime, nullable=False)
    repository_id = Column(Integer, ForeignKey('repositories.repository_id'), nullable=False)
    repository = relationship(
        'Repository',
        back_populates='changes',
        cascade='all, delete, delete-orphan',
        single_parent=True
    )

    def __repr__(self):
        return '<Change(change_id=%r, author=%r, commit_time=%r, commit_message=%r' % (
            self.change_id, self.author, self.commit_time, self.commit_message
        )


class Path(DeclarativeBase):
    """
    A versioned path.
    """
    __tablename__ = 'paths'
    __table_args__ = (
        PrimaryKeyConstraint('change_id', 'path'),
    )
    repository_id = Column(Integer, ForeignKey('repositories.repository_id'), nullable=False)
    change_id = Column(String(CHANGE_ID_LENGTH), ForeignKey('changes.change_id'), nullable=False)
    path = Column(String(PATH_LENGTH), nullable=False)
    kind = Column(
        Enum('d', 'f'), nullable=False,
        doc='d=directory, f=file')
    action = Column(
        Enum('a', 'c', 'd', 'e', 'm'), nullable=False,
        doc='a=added, c=copied, d=deleted, e=edited, m=moved')
    base_change_id = Column(String(CHANGE_ID_LENGTH), ForeignKey('changes.change_id'))
    base_path = Column(String(PATH_LENGTH))

    #change = relationship(
    #    'Change',
    #    back_populates='paths',
    #    cascade='all, delete, delete-orphan',
    #    single_parent=True
    #)

    def __repr__(self):
        result = '<Path(action=%r, kind=%r, path=%r, repository_id=%r, change_id=%r' % (
            self.action, self.kind, self.path, self.repository_id, self.change_id
        )
        if self.base_change_id is not None:
            result += ', base_change_id=%r, base_path=%r' % (self.base_change_id, self.base_path)
        result += '>'
        return result


Repository.changes = relationship('Change', back_populates='repository')
#Change.paths = relationship('Path', back_populates='change')

def vcdb_session(engine_uri):
    assert engine_uri is not None
    engine = sqlalchemy.create_engine(engine_uri)
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
