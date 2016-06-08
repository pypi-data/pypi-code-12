

import datetime
import os
import PIL
import struct
import threading

from constants import *
from utils.appdirs import user_data_dir
from utils.sdk_utils import (print_and_log, ERROR, DEBUG, bytearray_to_image,
                             image_to_bytearray,
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
    myme_id = Column(type_=Integer, nullable=True) # Id of the face internal to MyMe application
    detected_time = Column(type_=DateTime, nullable=False,
                           default=datetime.datetime.now())
    signature = Column(type_=LargeBinary, nullable=False)
    person_id = Column(ForeignKey(column='person.id'))

    # this defines a one-to-many relation between the DbPerson and the DbFace objects
    # the cascade argumnet means every db operation is cascaded, so deleting a face from a
    # person object, would also delete it from the faces table, etc.
    # delete-orphan means un-refereced objects are deleted (like a face with no persons)
    # see more at http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#one-to-many
    person = relationship("DbPerson",
                        backref=backref("faces", cascade="all, delete-orphan"))

    def __init__(self, myme_id=None, detected_time=None, signature=None,
                 person_id=None):
        self.myme_id=myme_id
        if type(detected_time) is not datetime.datetime:
            self.detected_time = datetime.datetime.utcfromtimestamp(detected_time)
        else:
            self.detected_time = detected_time

        if signature is not None:
            self.signature = struct.pack('<{}b'.format(len(signature)), *signature)
        else:
            self.signature = None
        self.person_id=person_id

    def get_signature(self):
        if self.signature is None:
            return None
        else:
            return struct.unpack('<{}b'.format(len(self.signature)), str(self.signature))


class DbFaceImage(Base):
    __tablename__ = 'images'
    id = Column(type_=Integer, primary_key=True)
    detected_time = Column(type_= DateTime, nullable=False,
                           default=datetime.datetime.now())
    image = Column(type_=LargeBinary)
    person_id = Column(ForeignKey(column='person.id'))

    person = relationship("DbPerson",
                        backref=backref("images", cascade="all, delete-orphan"))


    def __init__(self, detected_time=None, image=None, person_id=None):
        if type(detected_time) in [float,int, long]:
            self.detected_time = datetime.datetime.utcfromtimestamp(detected_time)
        else:
            self.detected_time = detected_time
        if "PIL." in str(type(image)): # If image is a PIL Image instance
            try:
                self.image = image_to_bytearray(image)
            except Exception as ex:
                print_and_log('ERROR: Unable to convert PIL '
                              'image to bytearray. Image will not be '
                              'stored.', ERROR)
                self.image = None
        else:
            self.image = image
        self.person_id = person_id

    def get_image(self):
        if self.image is None:
            return None
        else:
            return bytearray_to_image(self.image)


class DbPerson(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    profile_picture = Column(LargeBinary)
    first_detected = Column(type_=DateTime, nullable=False,
                           default=datetime.datetime.now())
    last_detected = Column(type_=DateTime, nullable=False,
                           default=datetime.datetime.now())

    def __init__(self, name=None, profile_picture=None, first_detected=None,
                 last_detected=None):
        self.name = name
        if "PIL." in str(type(profile_picture)):
            try:
                self.profile_picture = image_to_bytearray(profile_picture)
            except Exception as ex:
                print_and_log('ERROR: Unable to convert profile_picture PIL '
                              'image to bytearray. Profile picture will not be '
                              'stored.', ERROR)
                self.profile_picture = None
        else:
            self.profile_picture = profile_picture
        if type(first_detected) in [long, float, int]:
            self.first_detected = datetime.datetime.utcfromtimestamp(first_detected)
        else:
            self.first_detected = first_detected
        if type(last_detected)  in [long, float, int]:
            self.last_detected = datetime.datetime.utcfromtimestamp(last_detected)
        else:
            self.last_detected = last_detected

        self.faces = []
        self.images = []


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

    def get_face_image_by_id(self, db_face_image_id):
        with self.lock:
            return self.session().query(DbFaceImage).get(db_face_image_id)

    def get_person_by_person_id(self, person_id):
        with self.lock:
            return self.session().query(DbPerson).get(person_id)

    def remove_person_by_person_id(self, person_id):
        db_person = self.get_person_by_person_id(person_id)
        self.remove(db_person)

    def remove_face_by_face_id(self, face_id):
        db_face = self.get_face_by_face_id(face_id)
        self.remove(db_face)

    def get_all_faces_from_time(self, start_time, end_time):
        with self.lock:
            db_faces = self.session().query(DbFace).filter(
                    and_(DbFace.detected_time >  start_time,
                    DbFace.detected_time <  end_time)
            )
            return db_faces

    def get_face_images_for_person(self, person_id):
        db_person = self.get_person_by_person_id(person_id)
        if db_person is None:
            print_and_log('ERROR: Didn\'t find person with provided person_id '
                          '({}) in the DB.'.format(person_id), ERROR)
            return None
        return db_person.images

    def add_face_image_to_person(self, myme_face_image, person_id):

        db_person = self.get_person_by_person_id(person_id)
        if db_person is None:
            print_and_log('ERROR: Didn\'t find person with provided person_id '
                          '({}) in the DB.'.format(person_id), ERROR)
            return False

        # NOTE: DO NOT set myme_id=myme_face.id because this is wrong.
        # myme_face.id is an old id of the face when it was in stored in the DB
        # since above face wasn't found in the DB, it means it has been erased
        # since too much has passed without face being added to any person
        db_face_image = DbFaceImage(detected_time=myme_face_image.detected_time,
                             image=myme_face_image.image, person_id=person_id)
        self.add_and_commit(db_face_image)
        return True


    def remove_image_of_person(self, person_id, face_image_id):
        db_person = self.get_person_by_person_id(person_id)
        if db_person is None:
            print_and_log('ERROR: Didn\'t find person with provided person_id '
                          '({}) in the DB.'.format(person_id), ERROR)
            return False
        db_face_image = self.get_face_image_by_id(face_image_id)
        if db_face_image is None:
            print_and_log('ERROR: Didn\'t find face image with id: {} belonging '
                'to person with id: {}'.format(face_image_id, person_id), ERROR)
            return False
        self.remove(db_face_image)
        return True


    def remove_all_images_of_person(self, person_id):
        db_person = self.get_person_by_person_id(person_id)
        if db_person is None:
            print_and_log('ERROR: Didn\'t find person with provided person_id '
                          '({}) in the DB.'.format(person_id), ERROR)
            return False
        ids_to_remove = [img.id for img in db_person.images]
        for id in ids_to_remove:
            self.remove(self.get_face_image_by_id(id))
        return True


    def delete_face_from_db(self, db_face_id):
        db_face = self.get_face_by_face_id(db_face_id)
        if db_face is not None:
            self.remove(db_face)


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


    def delete_db(self):
        """
        deletes all the tables in the database(!).
        :return:
        """
        Base.metadata.drop_all()
        self._create_tables()
        self.commit_db()