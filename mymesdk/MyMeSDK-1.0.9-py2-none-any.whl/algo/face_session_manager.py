
import sys
import threading
import time

from ..database_manager import *
from face_session import FaceSession
from ..utils.sdk_utils import db_person_to_myme_person

class FaceSessionMananger():

    THREAD_WAIT_TIME_SEC = 5
    SIGANTURE_LEN        = 128
    MAX_SESSION_SIZE = 50
    MAX_IDLE_SEC = 60
    MAX_INACTIVE_SEC = 36000 # 10 hours currently

    def __init__(self, db_manager):
        """
        Initializes the FaceSessionMananger
        :param db_manager: Instance of the database manager shared across the SDK
        """
        self.db_manager = db_manager

        # When a session is active, it is considered as one of the candidates
        # for each incoming face.
        self.active_sessions = [] # list of FaceSession objects
        # An inactive session is no longer taken in acount for newly arriving
        # faces, however it stays alive for FaceSessionManager.MAX_INACTIVE_SEC
        # so that the user can use it to create a new person at a later time.
        self.inactive_sessions = [] # list of FaceSession objects
        self.face_id_to_session = dict()


    def stop(self):
        """
        Closes all sessions
        """
        for session in (self.active_sessions + self.inactive_sessions):
            self.close_session(session)


    def deactivate_idle_sessions(self):
        print_and_log('Deactivating idle sessions')
        active_sessions_upd = []
        for session in self.active_sessions:
            if time.time() - session.last_face_added_timestamp > self.MAX_IDLE_SEC:
                print_and_log('SESSION EXPIRED - moving to inactive.\n'
                    'Session face ids: {}'
                    ''.format(', '.join(str(x) for x in session.db_face_ids)))
                session.active = False
                self.inactive_sessions.append(session)
            else:
                active_sessions_upd.append(session)
        self.active_sessions = active_sessions_upd


    def delete_inactive_sessions(self):
        print_and_log('Deleting expired sessions')
        inactive_sessions_upd = []
        for session in self.inactive_sessions:
            if time.time() - session.last_face_added_timestamp > self.MAX_INACTIVE_SEC:
                self.close_session(session)
                print_and_log('Deleting expired session.')
            else:
                inactive_sessions_upd.append(session)
        self.inactive_sessions = inactive_sessions_upd


    def find_matching_person_for_face_id(self, face_id):
        """

        :param face_id:
        :return:
        """
        session = self.face_id_to_session.get(face_id, None)
        if session is None: # face part of deleted session or invalid face_id
            print_and_log('face_id: {} is not part of any active or inactive '
                          'sessions'.format(face_id))
            return None, 0.0, False

        db_person, prob = session.find_best_person_for_session()
        if db_person is not None:
            return db_person, prob, False
        elif session.size() >= FaceSession.MIN_SIZE_TO_CREATE_NEW_PERSON:
            return None, 0.0, True
        else:
            return None, 0.0, False


    def create_person_with_face_id(self, face_id, name=None):
        """
        Creates person out of session containing face_id, and deletes the sesssion.
        If session containing face_id is not found do nothing.

        :param face_id: ID of face whose session to turn into a person
        :param name: optional person name
        :return: newly created db_person
        """
        session = self.face_id_to_session.get(face_id, None)
        if session is None: # face part of expired session or invalid face_id
            return None

        for id in session.db_face_ids:
            self.face_id_to_session.pop(id, None)
        db_person = session.create_new_person_and_close(name)
        print_and_log('Created new person id: {}, with face ids: {}, '
                      'Deleting session.'
                      ''.format(db_person.id,
                            ', '.join(str(id) for id in session.db_face_ids)))

        if session.active:
            self.active_sessions.remove(session)
        else:
            self.inactive_sessions.remove(session)
        return db_person

    def find_best_active_session_for_sig(self, signature):
        """
        Finds and returns the session in active_sessions with the signature
        closest to the current signature.
        Or, if no session with a close enough signature exists, creates a new
        session
        :param signature: Face signature (array of ints)
        :return: index of session into which signature should be inserted
        """
        curr_session_idx = None

        # go over list of sessiosn
        min_dist_to_session = sys.float_info.max
        min_session_idx = None
        for i, session in enumerate(self.active_sessions):
            # get average distance of the signature to the session
            cur_distance_to_session = session.get_sig_to_session_score(signature)
            if  cur_distance_to_session < min_dist_to_session:
                min_dist_to_session = cur_distance_to_session
                min_session_idx = i

        # use the closest one if it's close enough (smaller than FaceSession.THRESHOLD_FACE_TO_SESSION)
        if min_dist_to_session <= FaceSession.THRESHOLD_FACE_TO_SESSION:
            print_and_log('Found matching session! (dist: {})'.format(min_dist_to_session), DEBUG)
            return min_session_idx

        # otherwise open a new session
        print_and_log('No matching session found (dist to closest: {}). '
                      'Opening a new session.'.format(min_dist_to_session), DEBUG)
        self.active_sessions.append(FaceSession(self.db_manager))
        min_session_idx = len(self.active_sessions) - 1
        return min_session_idx


    def add_face_to_session(self, myme_face_id, detected_time, signature):
        """
        Attaches newly detected face to a session.
        First, looks for a matching existing (active session).
        If not found, creates a new session.

        :param myme_face_id: Id of the face internal to MyMe application
                             will be stored in the database to enable later
                             fetching of image for the face
        :param detected_time: Time when face was deteced by MyMe
        :param signature: Signature of the detected faces (array of 128 ints)
        """

        # Mark as inactive all sessions that haven't been updated in more
        # than MAX_IDLE_SEC
        self.deactivate_idle_sessions()
        # Delete all sessions that have been inactive for more than
        # MAX_INACTIVE_SEC
        self.delete_inactive_sessions()

        # Find best session (this might open a new session if needed)
        curr_session_idx = self.find_best_active_session_for_sig(signature)
        curr_session = self.active_sessions[curr_session_idx]
        print_and_log('Found best session for current face (session id: {})'
                      ''.format(curr_session_idx))

        # Add face to the best session and return a MyMeFace object holding the face
        # Note that myme_face.id is the face's id in the DB, and not
        # where as the argument myme_face_id is the face's id internal to
        # the MyMe device.
        print_and_log('Add face to found session')
        myme_face = curr_session.add_face(myme_face_id, detected_time, signature)
        self.face_id_to_session[myme_face.id] = curr_session

        # Close session if too big (will try to find matching person to add session to)
        if len(curr_session.db_face_ids) > self.MAX_SESSION_SIZE:
            print_and_log('Closing session id {} because it\'s too big.'
                          ''.format(curr_session_idx))
            self.close_session(curr_session)
            del self.active_sessions[curr_session_idx]

        return myme_face

    def close_session(self, session):
        """
        Removes all session faces from face_id_to_session dict, and calls the
        session's close() function
        :param session:
        :return:
        """
        print_and_log('closing session with {} faces'
                          ''.format(len(session.db_face_ids)))

        for id in session.db_face_ids:
            self.face_id_to_session.pop(id, None)
        session.close()
