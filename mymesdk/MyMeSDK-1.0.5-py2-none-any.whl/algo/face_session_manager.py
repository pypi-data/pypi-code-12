
import sys
import threading
import time

from ..database_manager import *
from face_session import FaceSession
from ..utils.sdk_utils import db_person_to_myme_person

class FaceSessionMananger():

    THREAD_WAIT_TIME_SEC = 5
    SIGANTURE_LEN        = 128
    SESSION_MATCHING_THRESHOLD = 25.65
    MAX_SESSION_SIZE = 50
    MAX_IDLE_SEC = 60

    def __init__(self, db_manager, auto_create_new_person=True):
        """
        Initializes the FaceSessionMananger
        :param db_manager: Instance of the database manager shared across the SDK
        :param auto_create_new_person:
                (Boolean) if True - a new MyMePerson will be automatically
                created and added to the DB whenever 5 or more faces are
                received in a single session, and no matching person is found
                if False - the faces will be stored without a matching person.
        """
        self.db_manager = db_manager
        self.auto_create_new_person = auto_create_new_person

        self.open_sessions = [] # list of FaceSession

    def stop(self):
        """
        Closes all sessions
        """
        for session in self.open_sessions:
            session.close()

    def close_expired_sessions(self):
        for i, session in enumerate(self.open_sessions):
            if time.time() - session.last_face_added_timestamp > self.MAX_IDLE_SEC:
                session.close()
                del self.open_sessions[i]

    def find_best_session_for_sig(self, signature):
        """
        Finds and returns the session in open_sessions with the signature
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
        for i, session in enumerate(self.open_sessions):
            # get average distance of the signature to the session
            cur_distance_to_session = session.get_sig_to_session_score(signature)
            if  cur_distance_to_session < min_dist_to_session:
                min_dist_to_session = cur_distance_to_session
                min_session_idx = i

        # use the closest one if it's close enough (smaller than SESSION_MATCHING_THRESHOLD)
        if min_dist_to_session <= self.SESSION_MATCHING_THRESHOLD:
            print_and_log('Found matching session! (dist: {})'.format(min_dist_to_session), DEBUG)
            return min_session_idx

        # otherwise open a new session
        print_and_log('No matching session found (dist to closest: {}). Opening a new '
               'session.'.format(min_dist_to_session), DEBUG)
        self.open_sessions.append(FaceSession(self.db_manager))
        min_session_idx = len(self.open_sessions) - 1
        return min_session_idx


    def add_face_to_session(self, myme_face_id, detected_time, signature):
        """
        Update the current session with a newly detected face.
        If face is added to a session that has >= 3 faces and has no
        matching person, a new person is created containing the session's faces
        and the session is closed. <new_person_created> is True in such case.
        :param myme_face_id: Id of the face internal to MyMe application
                             will be stored in the database to enable later
                             fetching of image for the face
        :param detected_time: Time when face was deteced by MyMe
        :param signature: Signature of the detected faces (array of 128 ints)
        """
        # 0. Close all sessions that haven't been updated in more than MAX_IDLE_SEC
        self.close_expired_sessions()

        # 1. find best session (this might open a new session if needed)
        curr_session_idx = self.find_best_session_for_sig(signature)
        curr_session = self.open_sessions[curr_session_idx]

        # 2. add face to the best session and return a MyMeFace object holding the face
        myme_face = curr_session.add_face(myme_face_id, detected_time, signature)

        # 3. find person most closely matching curr_session or None if not found w/in a threshold
        matching_db_person, probability = curr_session.find_best_person_for_sigs()
        if matching_db_person is not None:
            print_and_log('found best person for current session, person id: ' \
                  '{}, probablity of match: {}%' \
                  ''.format(matching_db_person.id, probability), DEBUG)
        else:
            print_and_log('didn\'t find any people matching current session', DEBUG)

        # 4. Close session if needed (will create new person if no matching
        #    person exists already and auto_create_new_person = True)
        new_person_created = False
        if (self.auto_create_new_person == True and
            matching_db_person is None and
            len(curr_session.db_face_ids) >= FaceSession.MIN_SIZE_TO_CREATE_NEW_PERSON):
            print_and_log('Creating new person for current session and closing session', DEBUG)
            curr_session.create_person_and_close()
            new_person_created = True
            matching_db_person = self.db_manager.get_person_by_person_id(curr_session.db_person_id)
            probability = curr_session.db_probability
            del self.open_sessions[curr_session_idx]
        elif len(curr_session.db_face_ids) >= self.MAX_SESSION_SIZE:
            curr_session.close()
            del self.open_sessions[curr_session_idx]


        # 5. Return
        myme_person = None
        if matching_db_person is not None:
            myme_person = db_person_to_myme_person(matching_db_person)
        return myme_face, myme_person, probability, new_person_created

