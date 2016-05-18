
#from scipy.spatial.distance import cdist

import numpy as np
import time

from ..database_manager import DbPerson, DbFace
from ..myme_objects import MyMeFace
from ..utils.sdk_utils import (print_and_log, ERROR, EXCEPTION, DEBUG)

class FaceSession(object):
    MIN_SIZE_TO_CREATE_NEW_PERSON = 5
    DETECTOR_THRESHOLD=6.5
    CLARITY_THRESHOLD=22.5
    THRESHOLD_FACE_SESSION=25.65
    SESSION_TO_PERSON_THRESHOLD=27.3
    SIGNATURE_LEN = 128.

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.db_face_ids = [] # List of faces id in current session
        self.db_person_id = None # dbPerson id that most closely matches the session's sigs
        self.db_person_prob = 0 # Probability that this session matches <person>
        self.session_sigs_2d_nparray = np.empty((0, int(self.SIGNATURE_LEN)), np.uint8)

        # Session is closed when 60 seconds pass since last face is added
        self.last_face_added_timestamp = time.time()

    def add_face(self, myme_face_id, detected_time, signature):
        """
        Adds a new face to the current session. Additionally, the face is
        added to the databse, and the DbFace object is refreshed.
        This is done so that the database always contains all currently active
        faces. This is useful in case where the user myme_requests to get all faces.
        Also, by adding the face to the databse, the face gets a unique id
        which the user can then use to fetch an image for the face
        (the user will use the database id to access the face, while internally
        the SDK will use the myme_id to request an image from MyMe application)
        :param myme_face_id: Id of the face internal to MyMe application
                             will be stored in the database to enable later
                             fetching of image for the face
        :param detected_time: Time when face was deteced by MyMe
        :param signature: Signature of the detected faces (array of 128 ints)
        :return MyMeFace object representing the newly added face
        """
        db_face = DbFace(myme_id=myme_face_id,
                         detected_time=detected_time,
                         signature=signature)
        self.db_manager.add_and_commit(db_face)
        self.db_face_ids.append(db_face.id)
        self.last_face_added_timestamp = time.time()
        self.session_sigs_2d_nparray = \
            np.vstack([self.session_sigs_2d_nparray, np.array(signature)])

        return MyMeFace(id=db_face.id, detected_time=detected_time,
                        signature=signature)

    def close(self):
        """
        Close the session.
        On session closure one of two things can happen:
            1. Ignore (less than 3 face signatures in the session)
            2. Session faces are added to the DB and db_person is updated with
               all the new faces
        """
        print_and_log('closing session', DEBUG)

        # get a list of db faces objects using the ids list
        db_faces = [self.db_manager.get_face_by_face_id(face_id) for face_id in self.db_face_ids]

        if len(self.db_face_ids) < self.MIN_SIZE_TO_CREATE_NEW_PERSON:
            # Remove the faces
            for face in db_faces:
                self.db_manager.remove(face)
            self.db_manager.commit_db()
            return


        if self.db_person_id is not None:
            for db_face in db_faces:
                db_face.person_id = self.db_person_id

        self.db_manager.commit_db()


    def create_person_and_close(self):
        # Create new person if no person has been matched to session faces
        db_person = DbPerson()
        self.db_manager.add_and_commit(db_person)
        self.db_person_id = db_person.id
        # Person created specifically for current faces to probability of match
        # is trivially 100%
        self.db_probability = 100
        self.close()


    def sig_list_to_2d_numpy_array(self, siglist):
        '''
        Given a regular list k of signatures of from:
        [ [a1,..,a128],...,[k1,...,k128] ]

        1. Converts it to a list of numpy arrays:
        [ np.array([a1,a2,...,a128]), ,..... ,np.array([z1,z2,....,z128]) ]

        2. And then creates and returns a 2D numpy array of signatures

        The returned matrix is of dimension N x 128 (where N is the number of
        signatures in the current session)
        np.array([a1,a2,..,a128],
                 [b1,b2,..,b128],
                 .
                 .
                 [k1,k2,..,k128])
        :param siglist:
        :return: 2D numpy array of signatures
        '''
        # Convert siglist to a list of numpy arrays:
        sigs_np_array = [np.array(sig) for sig in siglist]

        # Create a 2D numpy array of signatures
        sigs_2d_np_array = \
                np.concatenate([sig[np.newaxis, :] for sig in sigs_np_array])
        return sigs_2d_np_array


    def compare_session_sigs_to_person_sigs(self, session_sigs_2d_np_array,
                                                  person_sigs_2d_np_array):
        """
        :param session_sigs_2d_np_array: N x 128 matrix of signatures
                 (where N is the number of signatures in the current session)
        :param person_sigs_np_array: M x 128 matrix of signatures
                 (where M is the number of signatures stored for current person)
        :return: score
        """
        # N x M distance matrix
        dist_matrix = self.calc_distances(
                session_sigs_2d_np_array, person_sigs_2d_np_array)
        # Computes the 40th percentile value between flattened dist_matrix
        score = np.percentile(dist_matrix, 40, interpolation='linear')
        return score


    def calc_distances(self, sigs_2d_np_array1, sigs_2d_np_array2):
        """
        Caluclates the L1 (aka 'cityblock') distance between the two given
        signature matricies
        :param sigs_2d_np_array1: N x 128 matrix of signatures
        :param sigs_2d_np_array2: M x 128 matrix of signatures
        :return: N x M distance matrix A,
                 where [Aij] = dist(array1[i], array2[j])
        """
        N = sigs_2d_np_array1.shape[0]
        M = sigs_2d_np_array2.shape[0]
        output = np.zeros((N,M))
        for m in range(M):
            for n in range(N):
                v1 = sigs_2d_np_array1[n,:]
                v2 = sigs_2d_np_array2[m,:]
                output[n,m] = np.sum(np.abs(v1-v2))

        output = output/float(self.SIGNATURE_LEN)

        # the following does the same using scipy, not used here for better compatabilty with windows
        # return (cdist(sigs_2d_np_array1, sigs_2d_np_array2, metric='cityblock')
        #         / self.SIGNATURE_LEN)

        return output


    def find_best_person_for_sigs(self):
        """
        Looks for a person from all people stored in the database that most
        closely matches the current session.
        :return: the person most closely matching faces in the session, or None
                 if no person matches within a SESSION_TO_PERSON_THRESHOLD
        """

        min_dist = 10e9
        best_person = None
        people_list = self.db_manager.get_all_people()
        for person in people_list:
            person_faces = person.faces
            person_sigs = [face.get_signature() for face in person_faces]
            if len(person_sigs) == 0:
                continue
            # Convert person_sigs to a 2d numpy array:
            person_sigs_2d_nparray = self.sig_list_to_2d_numpy_array(person_sigs)
            curr_person_dist = self.compare_session_sigs_to_person_sigs(
                        self.session_sigs_2d_nparray, person_sigs_2d_nparray)
            print_and_log('dist of person id {} to session sigs: {}'.
                          format(person.id, curr_person_dist), DEBUG)

            if curr_person_dist < min_dist:
                min_dist = curr_person_dist
                best_person = person

        if (min_dist <= self.SESSION_TO_PERSON_THRESHOLD):
            self.db_person_id = best_person.id
            self.db_person_prob = 100 - min_dist
            return best_person, self.db_person_prob
        else:
            self.db_person_id = None
            self.db_person_prob = 0
            return None, 0

    def get_sig_to_session_score(self, signature):
        """
        Calculates the match score between <signature> and
        signatures stored in the current session
        :param signature: Face signature (int array)
        """
        dists = self.calc_distances(np.array([signature]),
                                    self.session_sigs_2d_nparray)
        score = dists.mean()
        print_and_log('score of sig to session: {}'.format(score), DEBUG)
        return score