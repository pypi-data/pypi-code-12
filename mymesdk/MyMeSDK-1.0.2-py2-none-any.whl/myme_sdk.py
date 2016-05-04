__version__="1.0.0"

import cPickle
import datetime
import os
import Queue
import signal
import struct
import time
import traceback

from threading import Thread
import sys

from algo.face_session_manager import FaceSessionMananger
from bluetooth.bluetooth_manager import BluetoothManager
from constants import *
from database_manager import *
from delegates import MyMeDelegates
from user_callback_req_types import *
from utils.sdk_utils import db_face_to_myme_face, db_person_to_myme_person, INFO, DEBUG, ERROR
from utils.appdirs import user_data_dir
from myme_device import MyMeData
from myme_data_objects import MyMeFace, MyMePerson

class MyMeSDK(object):
    """
    The MyMeSDK class supplies the main interface to the MyMe Device.
    """
    _CONNECT_TIMEOUT = 7
    _SCAN_TIMEOUT = 5
    _APP_DATA_PATH = user_data_dir(appname=SDK_APPNAME, version=SDK_VERSION)
    _CONFIG_FILE_PATH = os.path.join(_APP_DATA_PATH, 'myme_sdk.config')
    def __init__(self):
        """
        MyMeDelegates class provides an interface for all the delegates that
        the user can redefine. For every delegate that the user wants to redefine,
        he must call the respective register_<delegate_name> function, and pass
        his own redefined delegate function.
        """
        signal.signal(signal.SIGINT, self._sigint_handler)

        self.delegate = MyMeDelegates()
        self.user_callback_thread_stop_event = threading.Event()
        self.user_callback_queue = Queue.Queue()
        self.user_callback_queue_lock = threading.Lock()
        self.user_callback_thread = Thread(target = self._user_callback_thread_entry)
        self.user_callback_thread.start()
        self.is_stopped = False

        # start the BluetoothManager
        self.bt_manager = BluetoothManager(
            sdk_charger_state_updated_cb = self._sdk_charger_state_updated_cb,
            sdk_device_tapped_cb = self._sdk_device_tapped_cb,
            sdk_battery_state_updated_cb = self._sdk_battery_state_updated_cb,
            sdk_battery_charge_level_updated_cb = self._sdk_battery_charge_level_updated_cb,
            sdk_device_state_updated = self._sdk_device_state_updated_cb,
            sdk_scan_complete_cb = self._sdk_scan_complete_cb,
            sdk_connected_to_device_cb = self._sdk_connected_to_device_cb,
            sdk_face_signature_cb = self._sdk_face_signature_cb,
            sdk_face_image_cb = self._sdk_face_image_cb,
            sdk_full_image_cb = self._sdk_full_image_cb,
            sdk_write_to_debug_cb = self._sdk_write_to_debug_cb,
            sdk_visual_topics_cb = self._sdk_visual_topics_cb,
            sdk_ocr_line_cb = self._sdk_ocr_line_cb,
            sdk_barcode_cb = self._sdk_barcode_cb)

        self.bt_manager.start() # start BT manager thread
        self._init_config_folder(self._APP_DATA_PATH)

        self.paired_device_addr = self._get_config_val_from_disk('paired_device_addr')

        if self.paired_device_addr is not None:
            self.bt_manager.set_device_state(DeviceState.Paired)

        # start DatabaseManager
        self.db_manager = DatabaseManager()

        # start FaceSessionMananger
        self.face_session_mananger = FaceSessionMananger(self.db_manager)

    def _user_callback_thread_entry(self):
        """
        This function is the entry point for a dedicated thread whose purpose
        is to call user callbacks (provided by user when calling one of the
        register_* functions). This is needed to prevent deadlock which may be
        caused by the user making SDK API calls from within his delegate
        functions
        """
        while not self.user_callback_thread_stop_event.is_set():
            try:
                item = self.user_callback_queue.get(timeout = 2)
                with self.user_callback_queue_lock:
                    self._handle_user_callback_queue_item(item)
                self.user_callback_queue.task_done()
            except Queue.Empty: # timeout
                continue

    def _handle_user_callback_queue_item(self, req):
        #print_and_log('handling request of type: {}'.format(req.type))
        if req.type == UserCallbackReqType.PairedDeviceStateUpdatedCbReq:
            self.delegate.PairedDeviceStateUpdated(req.new_state)
        elif req.type == UserCallbackReqType.FaceDetectedCbReq:
            self.delegate.FaceDetected(req.face, req.person, req.probability,
                                       req.is_last_face_in_frame)
        elif req.type == UserCallbackReqType.NewPersonCreatedCbReq:
            self.delegate.NewPersonCreated(req.person, req.timestamp)
        elif req.type == UserCallbackReqType.VisualTopicsReceivedCbReq:
            self.delegate.VisualTopicsReceived(req.topics, req.timestamp)
        elif req.type == UserCallbackReqType.OcrLineFoundCbReq:
            self.delegate.OcrLineFound(
                        req.myme_ocr_line, req.timestamp)
        elif req.type == UserCallbackReqType.BarcodeDetectedCbReq:
            self.delegate.BarcodeDetected(req.barcode, req.timestamp)
        elif req.type == UserCallbackReqType.ChargerStateUpdatedCbReq:
            self.delegate.ChargerStateUpdated(req.new_charger_state)
        elif req.type == UserCallbackReqType.DeviceTappedCbReq:
            self.delegate.DeviceTapped()
        elif req.type == UserCallbackReqType.BatteryStateUpdatedCbReq:
            self.delegate.BatteryStateUpdated(req.battery_state)
        elif req.type == UserCallbackReqType.BatteryChargeLevelChangedCbReq:
            self.delegate.BatteryChargeLevelChanged(req.battery_level)

        elif req.type == UserCallbackReqType.ScanCompleteCbReq:
            if req.user_callback is not None:
                req.user_callback(req.sorted_device_list, req.scan_state, req.error)
        elif req.type == UserCallbackReqType.ConnectedToDeviceCbReq:
            if req.user_callback is not None:
                req.user_callback(req.device_addr, req.error)
        elif req.type == UserCallbackReqType.FaceImageReceivedCbReq:
            if req.user_callback is not None:
                print 'calling user callback for new face image yay: {}'.format(req.user_callback)
                req.user_callback(req.myme_face)
        elif req.type == UserCallbackReqType.FullImageReceivedCbReq:
            if req.user_callback is not None:
                req.user_callback(req.myme_image)
        elif req.type == UserCallbackReqType.WriteToDebugCbReq:
            if req.user_callback is not None:
                req.user_callback(req.success)
        else:
            print_and_log('ERROR: GOT REQUEST OF UNKOWN TYPE: {}'.format(req.type))
            print('request data members: {}'.format(req.__dict__))

    def _sigint_handler(self, signum, frame):
        print_and_log('CTRL-C pressed. Will disconnect from device (if '
                      'connected), and exit.')
        self.stop()
        sys.exit(0)

    def __del__(self):
        self.stop()

    def _init_config_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    # ******************** BLUETOOTH MANAGER CALLBACKS *************************
    # Callback functions provided to the BluetoothManager to notify the SDK
    # when something occurs
    # **************************************************************************

    def _sdk_battery_charge_level_updated_cb(self, battery_level):
        self.user_callback_queue.put(BatteryChargeLevelChangedCbReq(battery_level))

    def _sdk_battery_state_updated_cb(self, new_battery_state):
        self.user_callback_queue.put(BatteryStateUpdatedCbReq(new_battery_state))

    def _sdk_charger_state_updated_cb(self, new_charger_state):
        self.user_callback_queue.put(ChargerStateUpdatedCbReq(new_charger_state))

    def _sdk_device_tapped_cb(self):
        self.user_callback_queue.put(DeviceTappedCbReq())

    def _sdk_device_state_updated_cb(self, new_state):
        self.user_callback_queue.put(PairedDeviceStateUpdatedCbReq(new_state))

    def _sdk_scan_complete_cb(self, sorted_device_list, scan_state, error,
                              user_callback):
        self.user_callback_queue.put(ScanCompleteCbReq(
                sorted_device_list, scan_state, error, user_callback))

    def _sdk_connected_to_device_cb(self, device_addr, error, cb):
        self.user_callback_queue.put(ConnectedToDeviceCbReq(
                device_addr, error, cb))

    def _sdk_visual_topics_cb(self, visual_topics, timestamp):
        self.user_callback_queue.put(VisualTopicsReceivedCbReq(
            topics=visual_topics, timestamp=timestamp))

    def _sdk_ocr_line_cb(self, ocr_line, timestamp, is_frame_end=False):
        self.user_callback_queue.put(OcrLineFoundCbReq(myme_ocr_line=ocr_line,
            timestamp=timestamp))

    def _sdk_barcode_cb(self, barcode, timestamp):
        self.user_callback_queue.put(BarcodeDetectedCbReq(
                barcode=barcode, timestamp=timestamp))

    def _sdk_face_signature_cb(self, detected_face_id, detected_time,
                               signature_int_array, is_last_face_in_frame = False):
        """
        Called by the bt manager whenever a new face signature is received
        Adds new face to the Faces DB

        :param detected_face_id: id of the detected face (application side id)
        :param detected_time: timestamp of when the detection occurred
                              (int seconds from epoch)
        :param signature_int_array: signature of the detected face stored as an
                                    array of integers
        :param: is_last_face_in_frame - True if this is the last face for this frame,
                false otherwise
        :return:
        """
        myme_face, myme_person, probability, new_person_created = \
            self.face_session_mananger.add_face_to_session(
                                    myme_face_id=detected_face_id,
                                    detected_time=detected_time,
                                    signature=signature_int_array)

        self.user_callback_queue.put(FaceDetectedCbReq(
                face=myme_face, person=myme_person, probability=probability,
                is_last_face_in_frame=is_last_face_in_frame))
        if new_person_created:
            self.user_callback_queue.put(NewPersonCreatedCbReq(
                    person=myme_person, timestamp=time.time()))


    def _sdk_face_image_cb(self, face_db_id, detected_time,
                           image_bytearray, user_callback):
        """
        Stores received image into the Faces DB with myme_face.db_id being the key
        :param face_myme_id: Id of face in the SDK DB for which image was fetched
        :param image_bytearray: Fetched image stored as a bytearray
        """
        self.db_manager.add_face_image_to_id(face_db_id, image_bytearray)
        myme_face = MyMeFace(id=face_db_id,
                         detected_time=detected_time,
                         face_image=bytearray_to_image(image_bytearray))
        self.user_callback_queue.put(FaceImageReceivedCbReq(
                myme_face, user_callback))

    def _sdk_full_image_cb(self, myme_image, user_callback):
        self.user_callback_queue.put(FullImageReceivedCbReq(
                myme_image, user_callback))

    def _sdk_write_to_debug_cb(self, success, user_callback):
        self.user_callback_queue.put(WriteToDebugCbReq(success, user_callback))

    # **************************************************************************
    # ************************* CONNECT, SCAN & PAIR ***************************
    # **************************************************************************
    def quick_connect(self):
        """
        This method scans for devices, pairs to the device that has the strongest
        signal and connects to it. It is blocking for the duration of the procedu
        :return: None
        """
        self.bt_manager.scan_for_peripherals_with_timeout(
                self._SCAN_TIMEOUT, True, self._cb_quick_connect_scan)

    def connect_to_paired_device_with_timeout(self, timeout_secs=_CONNECT_TIMEOUT,
                                              cb=None, block = True):
        """
        Connects to the paired device, In case connection fails, tries to
        reconnect until success or until <timeout_secs> pass.

        :param timeout: timeout time for connection request in seconds
        :param cb: (optional) callback function. Must be supplied in case block is False
        :param block: if True -blocks the caller until done, otherwise, returns immediately
        :return: None
        """
        if self.paired_device_addr is None:
            error = 'ERROR: You must first pair a device before connecting.'
            self._sdk_connected_to_device_cb(None, error, cb)
        else:
            self.bt_manager.connect_to_paired_device_with_timeout(
                    timeout_secs, self.paired_device_addr, cb, block)


    def disconnect_from_device(self):
        """
        Disconnects from the device

        :return True in case of success, false otherwise
        """
        self.bt_manager.disconnect_from_device()

    # TODO - add excpetion - cb must be suppiled when block is false
    # TODO - consider remove block or at least True by default
    def scan_for_devices_with_timeout(self, timeout_sec, block=True, cb=None):
        """
        This method scans for devices until <timeout_sec> pass.
        When done the ScanComplete delegate is called with the full list of detected devices

        :param timeout_sec: timeout in seconds
        :param block: if True, blocks until scan is done
        :param cb: Optional user callback function (if None, default is be used)
        """
        self.bt_manager.scan_for_peripherals_with_timeout(timeout_sec, block, cb)


    def _cb_quick_connect_scan(self, device_list, scan_state,
                               error=None, subscribe_to_all=True):
        """
        Calledback by bluetooth manager after a scan that was initiated by
        quick_connect

        :param device_list: List of devices.
        Each device is represented by dict with the following keys:
            "address" (device's MAC address)
            "name" (device name)
            "rssi" (signal strength)
        :param scan_result: scan compeltion reason (ScanState)
        :param subscribe_to_all: If true, device will subscribe to notifications
            from all available services
        :param error: in case of error, this string contains the error message
        :return:
        """
        if error:
            print error
        if device_list == []:
            print 'No devices found'
        else:
            self.pair_device(device_list[0]['address'])
            self.connect_to_paired_device_with_timeout(timeout_secs=7,
                                                       block=True)

    def _get_config_val_from_disk(self, key):
        """
        Fetches config value assigned to <key> from the app config file on disk

        :param key: key for the value to return from the config
        :return: value assigned to <key>, None if <key> not in config
        """
        if not os.path.exists(self._CONFIG_FILE_PATH):
            return None

        # NOTE: MUST OPEN PICKLED FILE WITH "b" MODE FOR WINDOWS COMPATABILITY
        with open(self._CONFIG_FILE_PATH, 'rb') as config_pickle:
            try:
                config_dict = cPickle.load(config_pickle)
                return config_dict.get(key, None)
            except Exception as ex:
                print "Didn't find stored config."
                return None


    def _store_config_val_to_disk(self, key, val):
        """
        Stores a new value into the application config file under <key>

        :param key: key for the value to store in the config
        :param val: value to store
        """
        # NOTE: MUST OPEN PICKLED FILE WITH "b" MODE FOR WINDOWS COMPATABILI    TY
        config_dict = {}
        if os.path.exists(self._CONFIG_FILE_PATH):
            with open(self._CONFIG_FILE_PATH, 'rb') as config_file:
                try:
                    config_dict = cPickle.load(config_file)
                except Exception as ex:
                    print "Didn't find stored config."
                    print 'Exception msg: {}'.format(ex)
                    traceback.print_exc()


        config_dict[key]=val
        with open(self._CONFIG_FILE_PATH, 'wb') as config_file:
            cPickle.dump(config_dict, config_file)

    def pair_device(self, device_addr):
        """
        This method saves the paired <device_addr> for future connection.
        Pairing must be done before connection.

        :param peripheral: Id the ID of the device to pair.
        :return: True if device_addr successfully stored, False otherwise
        """
        self.paired_device_addr = device_addr
        self.bt_manager.set_device_state(DeviceState.Paired)
        self._store_config_val_to_disk('paired_device_addr', device_addr)

    def clear_paired_device(self):
        self.paired_device_addr = None
        # TODO - why is this commented out?
        #self._store_config_val_to_disk('paired_device_addr', None)


    def get_paired_device_address(self):
        """
        :return: String containing the device address that was saved when pair_device() was called. Or None if no device has been paired
        """
        return self.paired_device_addr

    def get_device_connectivity_state(self):
        return self.bt_manager.get_device_state()

    # **************** MyMe Device Interaction Functions ***********************
    # Functions that request or send to various data from from/to the device
    # **************************************************************************

    # TODO - comment out
    def _write_to_debug(self, text_to_write, callback=None):
        """
         This method enables writing text to the device.
         :param text_to_write The text to be written to the device
         :param callback: optional callback function
        """
        self.bt_manager.write_to_debug(text_to_write, callback)

    def get_battery_charge_level(self, battery_charge_level_cb):
        """
        Gets the percent charge of the battery from the device

        """
        self.bt_manager.get_info_from_device(MyMeData.battery_charge_level,
                                             battery_charge_level_cb)

    def get_battery_state(self, battery_state_cb):
        """
        Get the BatteryState of the device battery. The possible values are:
                BatteryOK = 0
                BatteryCharging = 1
                BatteryLow = 2
                BatteryCritical = 3 # Device will shutdown upon reaching state

        :param battery_state_cb: callback function
        """
        self.bt_manager.get_info_from_device(MyMeData.battery_state,
                                             battery_state_cb)


    def get_charger_state(self, charger_state_cb):
        """
        Reads the charger state
        """
        self.bt_manager.get_info_from_device(MyMeData.charger_state,
                                             charger_state_cb)


    def get_device_time(self, device_time_cb):
        """
        Reads the time set on the connected device
        """
        self.bt_manager.get_info_from_device(MyMeData.device_time,
                                             device_time_cb)

    def get_device_hardware_version(self):
        return self.bt_manager.get_device_hardware_version()

    def get_device_software_version(self):
        return self.bt_manager.get_device_software_version()

    def _request_full_image(self, frame_idx, full_image_cb):
        """

        :param frame_idx: Index of frame for which to request a full image
        :param full_image_cb: callback function to be called after full image
                              request is handled
        """
        self.bt_manager.request_full_image(frame_idx, full_image_cb)


    # ******************* DATABASE INTERACTION FUNCTIONS ***********************
    # Functions that send or request data from the SDK database
    # **************************************************************************

    def get_all_people(self):

        """
        Returns a list with all the people that exist in the DB

        :return list of MyMePerson
        """
        return [db_person_to_myme_person(person) for person in
                self.db_manager.get_all_people()]

    # TODO - person - pass by id
    def set_name_to_person(self, my_me_person, name):
        """
        Sets the given name to the given my_me_person

        :param my_me_person: my_me_person object
        :param name: the nsame to set
        :return: None
        """
        db_person = self.db_manager.get_person_by_person_id(my_me_person.db_id)
        if db_person is None:
             print_and_log('ERROR: person id {0} does not exist'.
                           format(my_me_person.db_id), ERROR)
             return
        db_person.name = name
        self.db_manager.commit_db()

    # TODO - person - pass by id
    def set_profile_picture(self, my_me_person, profile_pic):
        """
        Sets the given profile picture to the given my_me_person.

        :param my_me_person: my_me_person object
        :param profile_pic: the prfoile picture to set
        :return: None
        """
        db_person = self.db_manager.get_person_by_person_id(my_me_person.db_id)
        db_person.profile_pic = profile_pic
        self.db_manager.commit_db()

    def get_person(self, person_id):
        """
        Fetches a person by Id from the DB, with his list of faces

        :param person_id: the person Id to fetch
        :return: MyMePerson or None if not found
        """
        return db_person_to_myme_person(
                (self.db_manager.get_person_by_person_id(person_id)))

    def remove_person(self, person_id):
        """
        Removes the given person from the DB,
         any person face(s) is(are) deleted as well

        :param person_id:
        :return:
        """
        db_person = self.db_manager.get_person_by_person_id(person_id)
        if db_person is not None:
            self.db_manager.remove(db_person)

    def associate_face(self, myme_face, myme_person):
        """
        Associates the given MyMeface with the given MyMePerson
        Note the preivouse association of the given face is removed from the relevant face

        :param myme_face: the face to associate
        :param myme_person: the person to associate with
        :return: None
        """
        db_person = self.db_manager.get_person_by_person_id(myme_person.db_id)
        if db_person is None:
            print_and_log('ERROR: person id {} does not exist'.
                          format(myme_person.db_id), ERROR)
            return
        db_face   = self.db_manager.get_face_by_face_id(myme_face.id)
        if db_face is None:
            print_and_log('ERROR: db face id {0} does not exist'.
                          format(myme_face.id), ERROR)
            return

        db_person.faces.append(db_face)
        self.db_manager.commit_db()

    def delete_face(self, face_id):
        """
        Deletes the given face from the DB
        The reference to the face from the relevant person is also deleted

        :param face_id: the face id to delete
        :return: None
        """
        db_face = self.db_manager.get_face_by_face_id(face_id)
        self.db_manager.remove(db_face)

    def get_all_faces_from_time(self, start_time, end_time):
        """
        Returns all MyMeFaces detected between start_time and end_time

        :param start_time: state time (DateTime object)
        :param end_time: end time (DateTime object)
        :return: list of faces matching the query
        """
        db_faces = self.db_manager.get_all_faces_from_time(start_time, end_time)
        return [db_face_to_myme_face(face) for face in db_faces]

    def get_all_faces(self):
        """
        Returns a list of all MyMeFace objects in the DB

        :return: list of all MyMeFace objects in the DB
        """
        return [db_face_to_myme_face(face) for face in
                self.db_manager.get_all_faces()]

    def request_image_for_face_id(self, db_face_id, face_image_cb):
        """
        Requests the image from the device that is associated with db_id.
        If the image arrives, it will be added automatically to the face DB.

        :param db_face_id: ID of the face in Faces DB
        :param face_image_cb: Callback function that receives the fetched face and optionally an error message
        :return:
        """
        db_face = self.db_manager.get_face_by_face_id(db_face_id)

        self.bt_manager.request_face_image(
                db_face_id=db_face_id,
                myme_face_id=db_face.myme_id,
                face_image_cb=face_image_cb)

    def register_paired_device_state_updated_cb(self, cb):
        self.delegate.PairedDeviceStateUpdated = cb

    def register_face_detected_cb(self, cb):
        self.delegate.FaceDetected = cb

    def register_new_person_created_cb(self, cb):
        self.delegate.NewPersonCreated = cb

    def _register_visual_topics_received_cb(self, cb):
        self.delegate.VisualTopicsReceived = cb

    def register_ocr_line_found_cb(self, cb):
        self.delegate.OcrLineFound = cb

    def register_device_tapped_cb(self, cb):
        self.delegate.DeviceTapped = cb

    def register_barcode_detected_cb(self, cb):
        self.delegate.BarcodeDetected = cb

    def stop(self):
        if not self.is_stopped:
            # stop the bluetooth manager, this would also disconnect from device and stop bgapi lib
            self.bt_manager.stop()

            # stop the user callback thread
            self.user_callback_thread_stop_event.set()
            self.user_callback_thread.join()

            # stop the user callback thread
            self.face_session_mananger.stop()

            self.is_stopped = True

    def _set_device_to_current_time(self):
        """
        TODO
        We should not expose the ability to set the device time to the user,
        it's internal, and in any case the SDK sets it to current time whenever
        it's connected and the time is off, so it would just cause confusion in
        cases the user sets the API to a different time.
        """
        raise NotImplementedError

    """
    /**
     Returns the person that has the best match to the specified face that the matching score is under the given score. (lower score means better match).
     @param face The MyMeFace that will be used to find the best match.
     @param score The score that the matching Person has to be under. we recommend to insert 2.5.
     @return The best matched MyMePerson, returns nil if no such person exists.
     */
    -(MyMePerson*_Nullable) bestPersonMatchForFace:(nonnull MyMeFace*)face underScore:(CGFloat)score;

    /**
     Calculates the matching score for all people in the DB to the given Face. (lower score means better match).
     @param face The face you want to detect possible matches.
     @param underScore People that there score is lower than this parameter will not be sent back. if you want to get all people insert here FLT_MAX.
     @return An array with Objects of type MatchedPersonData, each MatchedPersonData Object contains the Person ID and the matching score. if no matches found, return nil.
     @see MatchingData.h class
     */
    -(NSArray*_Nullable) detectPossibleMatchesFrom:(nonnull MyMeFace*)face underScore:(CGFloat)underScore;

    /**
     Calculates the similarity score of 2 Faces, as lower the score is the chances of a match are higher.
     @param face1 The first face you want to calculate similarity.
     @param face2 The second face you want to calculate similarity.
     @return CGFloat The matching score.
     */
    -(CGFloat) similarityOf:(nonnull MyMeFace*)face1 and:(nonnull MyMeFace*)face2;
    """