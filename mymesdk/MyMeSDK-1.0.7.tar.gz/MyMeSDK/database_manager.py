

import datetime
import os
import struct
import threading
from constants import *
from utils.appdirs import user_data_dir
from utils.sdk_utils import (print_and_log, ERROR, DEBUG, bytearray_to_image,
                            db_person_to_myme_person, db_face_to_myme_face)


from sqlalchemy import (Column, ForeignKey, Integer, String, LargeBinary,
                        Boolean, DateTime, and_, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref,sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

Base = declarative_base()

class DbFace(Base):
    __tablename__ = 'face'
    id = Column(type_=Integer, primary_key=True)
    myme_id = Column(type_=Integer, nullable=True) # Id of the face image internal to MyMe application
    detected_time = Column(type_=DateTime, nullable=False,
                           default=datetime.datetime.now())
    signature = Column(type_=LargeBinary, nullable=False)
    image = Column(type_=LargeBinary)
    image_fetch_failed = Column(type_=Boolean, nullable=False, default=False)
    person_id = Column(ForeignKey(column='person.id'))

    # this defines a one-to-many relation between the DbPerson and the DbFace objects
    # the cascade argumnet means every db operation is cascaded, so deleting a face from a
    # person object, would also delete it from the faces table, etc.
    # delete-orphan means un-refereced objects are deleted (like a face with no persons)
    # see more at http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-many
    person = relationship("DbPerson",
                        backref=backref("faces", cascade="all, delete-orphan"))

    def __init__(self, myme_id=None, detected_time=None, signature=None, image=None,
                 image_fetch_failed=None, person_id=None):
        self.myme_id=myme_id
        if type(detected_time) is not datetime.datetime:
            self.detected_time = datetime.datetime.utcfromtimestamp(detected_time)
        else:
            self.detected_time = detected_time


        if signature is not None:
            self.signature = struct.pack('<{}b'.format(len(signature)), *signature)
        else:
            self.signature = None
        self.image=image
        self.image_fetch_failed=image_fetch_failed
        self.person_id=person_id


    def get_signature(self):
        if self.signature is None:
            return None
        else:
            return struct.unpack('<{}b'.format(len(self.signature)), str(self.signature))

    def get_image(self):
        if self.image is None:
            return None
        else:
            return bytearray_to_image(self.image)


class DbPerson(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    profile_pic = Column(LargeBinary)

class DatabaseManager(object):
    MYME_DB_PATH = os.path.join(
            user_data_dir(appname=SDK_APPNAME, version=SDK_VERSION),
            MYME_DB_NAME)

    def __init__(self):

        print_and_log('database path {} '.
                           format(self.MYME_DB_PATH), DEBUG)
        self.lock = threading.Lock()

        db_url = "sqlite:///" + self.MYME_DB_PATH
        # Create an engine that stores data local folder (MYME_DB_PATH)
        # Note this can be changed to access other databases, also web databases
        if not os.path.exists(os.path.dirname(self.MYME_DB_PATH)):
            os.makedirs(os.path.dirname(self.MYME_DB_PATH))
        self.engine = create_engine(db_url, connect_args={'check_same_thread':False}, poolclass=StaticPool)

        # make sure tables are created
        self._create_tables()

        # Bind the engine to the metadata of the Base class so that the
        # declaratives can be accessed through a DBSession instance
        Base.metadata.bind = self.engine

        self.session_maker = sessionmaker(bind=self.engine)
        # Create a thread-local session
        # The ScopedSession object by default uses [threading.local()] as storage,
        # so that a single Session is maintained for all who call upon the
        # ScopedSession registry, but only within the scope of a single thread.
        # Callers who call upon the registry in a different thread get a Session
        # instance that is local to that other thread.
        # Using this technique, the ScopedSession provides a quick and relatively
        # simple way of providing a single, global object in an application that
        # is safe to be called upon from multiple threads.
        # TL;DR: SINCE DB IS USED ACROSS DIFFERENT THREADS, MUST USE SCOPED_SESSION

        # A DBSession() instance establishes all conversations with the database
        # and represents a "staging zone" for all the objects loaded into the
        # database session object. Any change made against the objects in the
        # session won't be persisted into the database until you call
        # session().commit(). If you're not happy about the changes, you can
        # revert all of them back to the last commit by calling
        # session().rollback()

        self.session = scoped_session(self.session_maker)

    def add(self, db_obj):
        with self.lock:
            self.session().add(db_obj)

    def refresh(self, db_obj):
        with self.lock:
            self.session().flush()
            self.session().refresh(db_obj)

    def add_and_refresh(self, db_obj):
        self.add(db_obj)
        self.refresh(db_obj)

    def add_and_commit(self, db_obj):
        with self.lock:
            self.session().add(db_obj)
            self.session().commit()

    def remove(self, db_obj):
        with self.lock:
            self.session().delete(db_obj)
            self.session().commit()

    def get_all_people(self):
        with self.lock:
            return self.session().query(DbPerson).all()

    def get_all_faces(self):
        with self.lock:
            return self.session().query(DbFace).all()

    def get_face_by_face_id(self, db_face_id):
        with self.lock:
            return self.session().query(DbFace).get(db_face_id)


    def get_person_by_person_id(self, person_id):
        with self.lock:
            return self.session().query(DbPerson).get(person_id)

    def remove_person_by_person_id(self, person_id):
        with self.lock:
            self.remove(self.get_person_by_person_id(person_id))
            self.session().commit()


    def get_all_faces_from_time(self, start_time, end_time):
        with self.lock:
            db_faces = self.session().query(DbFace).filter(
                    and_(DbFace.detected_time >  start_time,
                    DbFace.detected_time <  end_time)
            )
            return db_faces


    def add_face_image_to_id(self, db_faceid, image_bytearray):
        db_face = self.get_face_by_face_id(db_faceid)
        if db_face is None:
            print_and_log('ERROR: db_face id {0} does not exist'.
                           format(db_faceid), ERROR)
            return
        db_face.image = image_bytearray
        self.commit_db()

    def commit_db(self):
        """
        updates the DB with any pending changes (changes performed on any of
        the DbFaces/DbPerson instances)
        """
        with self.lock:
            self.session().commit()

    def _create_tables(self):
         # Create all tables in the engine (if not already exisiting)
        Base.metadata.create_all(self.engine)

    def _delete_db(self):
        """
        deletes all the tables in the database(!).
        :return:
        """
        Base.metadata.drop_all()
        self._create_tables()
        self.commit_db()