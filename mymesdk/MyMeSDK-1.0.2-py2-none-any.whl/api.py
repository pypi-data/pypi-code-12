__version__="1.0.0"

"""
The api module supplies the main interface to the MyMe Device.
This module is intended to be used with the BLED112 Bluetooth Smart Dongle:
https://www.bluegiga.com/en-US/products/bled112-bluetooth-smart-dongle/
"""

import cPickle
import datetime
import os
import Queue
import signal
import struct
import logging
import time
import traceback

import threading
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
from myme_objects import MyMeFace, MyMePerson
import atexit


_CONNECT_TIMEOUT = 7
_SCAN_TIMEOUT = 5
_APP_DATA_PATH = user_data_dir(appname=SDK_APPNAME, version=SDK_VERSION)
_CONFIG_FILE_PATH = os.path.join(_APP_DATA_PATH, 'myme_sdk.config')

_is_initialized=False

def initialize(verbose=False):
    """
    Initializes the SDK. This function must be called exactly once before using any other SDK API.

    :param verbose: when True, debug logs are printed to standard output.
    :return: None
    :raise: :class:`MyMeSDK.constants.MyMeException`.
    """

    # this catch the siginit singal handler and disconnects the device
    # disabled for now as it's quite annoying to the user
    #signal.signal(signal.SIGINT, _sigint_handler)

    global _is_initialized
    if _is_initialized:
        raise Exception('MyMeSDK api already initialized')

    global delegate
    global user_callback_thread_stop_event
    global user_callback_queue
    global user_callback_queue_lock
    global user_callback_thread
    global is_stopped
    global bt_manager
    global paired_device_addr
    global db_manager
    global face_session_mananger


    atexit.register(_stop)
    # setup logger
    _setup_logger(verbose)
    delegate = MyMeDelegates()
    user_callback_thread_stop_event = threading.Event()
    user_callback_queue = Queue.Queue()
    user_callback_queue_lock = threading.Lock()
    user_callback_thread = Thread(target = _user_callback_thread_entry)
    user_callback_thread.start()
    is_stopped = False

    # start the BluetoothManager
    bt_manager = BluetoothManager(
        sdk_charger_state_updated_cb = _sdk_charger_state_updated_cb,
        sdk_device_tapped_cb = _sdk_device_tapped_cb,
        sdk_battery_state_updated_cb = _sdk_battery_state_updated_cb,
        sdk_battery_charge_level_updated_cb = _sdk_battery_charge_level_updated_cb,
        sdk_device_state_updated = _sdk_device_state_updated_cb,
        sdk_scan_complete_cb = _sdk_scan_complete_cb,
        sdk_connected_to_device_cb = _sdk_connected_to_device_cb,
        sdk_face_signature_cb = _sdk_face_signature_cb,
        sdk_face_image_cb = _sdk_face_image_cb,
        sdk_full_image_cb = _sdk_full_image_cb,
        sdk_write_to_debug_cb = _sdk_write_to_debug_cb,
        sdk_visual_topics_cb = _sdk_visual_topics_cb,
        sdk_ocr_line_cb = _sdk_ocr_line_cb,
        sdk_barcode_cb = _sdk_barcode_cb)

    bt_manager.start() # start BT manager thread
    _init_config_folder(_APP_DATA_PATH)

    paired_device_addr = _get_config_val_from_disk('paired_device_addr')

    if paired_device_addr is not None:
        bt_manager.set_device_state(DeviceState.Paired)

    # start DatabaseManager
    db_manager = DatabaseManager()

    # start FaceSessionMananger
    face_session_mananger = FaceSessionMananger(db_manager)

    _is_initialized=True


def _setup_logger(verbose):
    root_logger = logging.getLogger()

    if verbose:
        formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.ERROR)

def _verify_initializing():
    if not _is_initialized:
        raise Exception("'MyMeSDK api was not initialized. Call api.initialize() first")


def _user_callback_thread_entry():
    """
    This function is the entry point for a dedicated thread whose purpose
    is to call user callbacks (provided by user when calling one of the
    register_* functions). This is needed to prevent deadlock which may be
    caused by the user making SDK API calls from within his delegate
    functions
    """
    while not user_callback_thread_stop_event.is_set():
        #print_and_log('In user_callback_thread_entry')
        try:
            item = user_callback_queue.get(timeout = 2)
            with user_callback_queue_lock:
                _handle_user_callback_queue_item(item)
            user_callback_queue.task_done()
        except Queue.Empty: # timeout
            continue

def _handle_user_callback_queue_item(req):
    #print_and_log('handling request of type: {}'.format(req.type))
    if req.type == UserCallbackReqType.PairedDeviceStateUpdatedCbReq:
        delegate.PairedDeviceStateUpdated(req.new_state)
    elif req.type == UserCallbackReqType.FaceDetectedCbReq:
        delegate.FaceDetected(req.face, req.person, req.probability,
                                   req.is_last_face_in_frame)
    elif req.type == UserCallbackReqType.NewPersonCreatedCbReq:
        delegate.NewPersonCreated(req.person, req.timestamp)
    elif req.type == UserCallbackReqType.VisualTopicsReceivedCbReq:
        delegate.VisualTopicsReceived(req.topics, req.timestamp)
    elif req.type == UserCallbackReqType.OcrLineFoundCbReq:
        delegate.OcrLineFound(
                    req.myme_ocr_line, req.timestamp)
    elif req.type == UserCallbackReqType.BarcodeDetectedCbReq:
        delegate.BarcodeDetected(req.barcode_type, req.barcode_value, req.timestamp)
    elif req.type == UserCallbackReqType.ChargerStateUpdatedCbReq:
        delegate.ChargerStateUpdated(req.new_charger_state)
    elif req.type == UserCallbackReqType.DeviceTappedCbReq:
        delegate.DeviceTapped()
    elif req.type == UserCallbackReqType.BatteryStateUpdatedCbReq:
        delegate.BatteryStateUpdated(req.battery_state)
    elif req.type == UserCallbackReqType.BatteryChargeLevelChangedCbReq:
        delegate.BatteryChargeLevelChanged(req.battery_level)

    elif req.type == UserCallbackReqType.ScanCompleteCbReq:
        if req.user_callback is not None:
            req.user_callback(req.sorted_device_list, req.scan_state, req.error)
    elif req.type == UserCallbackReqType.ConnectedToDeviceCbReq:
        if req.user_callback is not None:
            req.user_callback(error=req.error, device_addr=req.device_addr)
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

def _sigint_handler(signum, frame):
    print_and_log('CTRL-C pressed. Will disconnect from device (if '
                  'connected), and exit.')
    _stop()
    sys.exit(0)

#def __del__():
#    _stop()

def _init_config_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

# ******************** BLUETOOTH MANAGER CALLBACKS *************************
# Callback functions provided to the BluetoothManager to notify the SDK
# when something occurs
# **************************************************************************

def _sdk_battery_charge_level_updated_cb(battery_level):
    user_callback_queue.put(BatteryChargeLevelChangedCbReq(battery_level))

def _sdk_battery_state_updated_cb(new_battery_state):
    user_callback_queue.put(BatteryStateUpdatedCbReq(new_battery_state))

def _sdk_charger_state_updated_cb(new_charger_state):
    user_callback_queue.put(ChargerStateUpdatedCbReq(new_charger_state))

def _sdk_device_tapped_cb():
    user_callback_queue.put(DeviceTappedCbReq())

def _sdk_device_state_updated_cb(new_state):
    user_callback_queue.put(PairedDeviceStateUpdatedCbReq(new_state))

def _sdk_scan_complete_cb(sorted_device_list, scan_state, error,
                          user_callback):
    user_callback_queue.put(ScanCompleteCbReq(
            sorted_device_list, scan_state, error, user_callback))

def _sdk_connected_to_device_cb(device_addr, error, cb):
    user_callback_queue.put(ConnectedToDeviceCbReq(
            device_addr, error, cb))

def _sdk_visual_topics_cb(visual_topics, timestamp):
    user_callback_queue.put(VisualTopicsReceivedCbReq(
        topics=visual_topics, timestamp=timestamp))

def _sdk_ocr_line_cb(ocr_line, timestamp, is_frame_end=False):
    user_callback_queue.put(OcrLineFoundCbReq(myme_ocr_line=ocr_line,
        timestamp=timestamp))

def _sdk_barcode_cb(barcode_type, barcode_value, timestamp):
    user_callback_queue.put(BarcodeDetectedCbReq(
            barcode_type=barcode_type, barcode_value=barcode_value,
            timestamp=timestamp))

def _sdk_face_signature_cb(detected_face_id, detected_time,
                           signature_int_array, is_last_face_in_frame = False):
    """
    Called by the bt manager whenever a new face signature is received
    Adds new face to the Faces DB

    :param: detected_face_id: id of the detected face (application side id)
    :param: detected_time: timestamp of when the detection occurred
                          (int seconds from epoch)
    :param: signature_int_array: signature of the detected face stored as an
                                array of integers
    :param: is_last_face_in_frame - True if this is the last face for this frame,
            false otherwise
    :return:
    """
    myme_face, myme_person, probability, new_person_created = \
        face_session_mananger.add_face_to_session(
                                myme_face_id=detected_face_id,
                                detected_time=detected_time,
                                signature=signature_int_array)

    user_callback_queue.put(FaceDetectedCbReq(
            face=myme_face, person=myme_person, probability=probability,
            is_last_face_in_frame=is_last_face_in_frame))
    if new_person_created:
        user_callback_queue.put(NewPersonCreatedCbReq(
                person=myme_person, timestamp=time.time()))


def _sdk_face_image_cb(face_db_id, detected_time,
                       image_bytearray, user_callback):
    """
    Stores received image into the Faces DB with myme_face.db_id being the key
    :param: face_myme_id: Id of face in the SDK DB for which image was fetched
    :param: image_bytearray: Fetched image stored as a bytearray
    """
    db_manager.add_face_image_to_id(face_db_id, image_bytearray)
    myme_face = MyMeFace(id=face_db_id,
                     detected_time=detected_time,
                     face_image=bytearray_to_image(image_bytearray))
    user_callback_queue.put(FaceImageReceivedCbReq(
            myme_face, user_callback))

def _sdk_full_image_cb(myme_image, user_callback):
    user_callback_queue.put(FullImageReceivedCbReq(
            myme_image, user_callback))

def _sdk_write_to_debug_cb(success, user_callback):
    user_callback_queue.put(WriteToDebugCbReq(success, user_callback))

# **************************************************************************
# ************************* CONNECT, SCAN & PAIR ***************************
# **************************************************************************
def quick_connect():
    """
    This method scans for devices, pairs to the device that has the strongest
    signal and connects to it. It is blocking for the duration of the procedure.

    Returns:
         |  Tuple: (True/False, error_string).
         |  (True, None) is returned in case of a successful connection.
         |  False otherwise, in which case the error string contains the failure reason

    """
    _verify_initializing()
    sorted_device_list, scan_state, error = \
         bt_manager.scan_for_peripherals_with_timeout(_SCAN_TIMEOUT)

    if error:
        return False, error
    if sorted_device_list == []:
        return False, 'No devices found'
    else:
        pair_device(sorted_device_list[0]['address'])
        return connect_to_paired_device()

def connect_to_paired_device():
    """
    Connects to the paired device. In case connection fails, tries to
    reconnect until success. It is blocking for the duration of the procedure.

    :return: None
    """
    _verify_initializing()
    if paired_device_addr is None:
        error = 'ERROR: You must first pair a device before connecting.'
        return False, error
    else:
        return bt_manager.connect_to_paired_device_with_timeout(
                _CONNECT_TIMEOUT, paired_device_addr, None, True)

def disconnect_from_device():
    """
    Disconnects from the device which is currently connected.

    :return: True in case of success, False otherwise

    """
    _verify_initializing()
    return bt_manager.disconnect_from_device()

# TODO - add excpetion - cb must be suppiled when block is false
# TODO - consider remove block or at least True by default

def scan_for_devices_with_timeout(timeout_sec):
    """
    This method scans for devices until <timeout_sec> pass and returns the result.

    :param: timeout_sec: duration of seconds to perform the scan.

    Returns:

    | Tuple: (sorted_device_list, scan_state, error)


    | sorted_device_list - list of devices sorted by RSSI (lower value means device is closer). Each device is a dictionary with the following keys::

        'address': device bluetooth address
        'name': device name
        'rssi': device rssi

    | scan_state one of :class:`MyMeSDK.constants.ScanState`.
    | error - None on success, string representing the error in case of failure.

    """
    _verify_initializing()
    return bt_manager.scan_for_peripherals_with_timeout(timeout_sec)


def _get_config_val_from_disk(key):
    """
    Fetches config value assigned to <key> from the app config file on disk

    :param: key: key for the value to return from the config
    :return: value assigned to <key>, None if <key> not in config
    """
    if not os.path.exists(_CONFIG_FILE_PATH):
        return None

    # NOTE: MUST OPEN PICKLED FILE WITH "b" MODE FOR WINDOWS COMPATABILITY
    with open(_CONFIG_FILE_PATH, 'rb') as config_pickle:
        try:
            config_dict = cPickle.load(config_pickle)
            return config_dict.get(key, None)
        except Exception as ex:
            print_and_log("Didn't find stored config.", ERROR)
            return None


def _store_config_val_to_disk(key, val):
    """
    Stores a new value into the application config file under <key>

    :param: key: key for the value to store in the config
    :param: val: value to store
    """
    # NOTE: MUST OPEN PICKLED FILE WITH "b" MODE FOR WINDOWS COMPATABILI    TY
    config_dict = {}
    if os.path.exists(_CONFIG_FILE_PATH):
        with open(_CONFIG_FILE_PATH, 'rb') as config_file:
            try:
                config_dict = cPickle.load(config_file)
            except Exception as ex:
                print_and_log("Didn't find stored config.", ERROR)
                print_and_log('Exception msg: {}'.format(ex), ERROR)
                traceback.print_exc()

    config_dict[key]=val
    with open(_CONFIG_FILE_PATH, 'wb') as config_file:
        cPickle.dump(config_dict, config_file)

def pair_device(device_addr):
    """
    This method saves the given device_addr for future connection.
    Pairing must be done before connection.

    :param: peripheral: device_addr - the device address to pair with. (the 'address' key of the device dict returned by function :meth:`MyMeSDK.api.scan_for_devices_with_timeout`
    :return: True if device_addr successfully paired, False otherwise
    """
    _verify_initializing()
    paired_device_addr = device_addr
    bt_manager.set_device_state(DeviceState.Paired)
    _store_config_val_to_disk('paired_device_addr', device_addr)

def clear_paired_device():
    """
    Clears paired device (if such one exists)

    :return: None
    """
    _verify_initializing()
    global paired_device_addr
    paired_device_addr = None
    _store_config_val_to_disk('paired_device_addr', None)


def get_paired_device_address():
    """
    Gets the paired device address

    :return: String containing the device address that was saved when pair_device() was called, or None if no device has been paired
    """
    _verify_initializing()
    return paired_device_addr

def get_device_connectivity_state():
    """
    Gets the device connection state

    :return: One of the device states :class:`MyMeSDK.constants.DeviceState`
    """
    _verify_initializing()
    return bt_manager.get_device_state()

# **************** MyMe Device Interaction Functions ***********************
# Functions that request or send to various data from from/to the device
# **************************************************************************
def _write_to_debug(text_to_write, callback=None):
    """
     This method enables writing text to the device.
     :param text_to_write The text to be written to the device
     :param callback: optional callback function
    """
    _verify_initializing()
    bt_manager.write_to_debug(text_to_write, callback)

def get_battery_charge_level():
    """
    Gets the percent charge of the battery from the device.

    :return: device charge level, in percentage between 0 to 100.
    """
    _verify_initializing()
    return bt_manager.get_info_from_device(MyMeData.battery_charge_level)

def get_battery_state():
    """
    Get the BatteryState of the device battery. The possible values are::

        BatteryOK = 0
        BatteryCharging = 1
        BatteryLow = 2
        BatteryCritical = 3 # Device will shutdown upon reaching state

    :return: device battery state, one of :class:`MyMeSDK.constants.BatteryState`
    """
    _verify_initializing()
    return bt_manager.get_info_from_device(MyMeData.battery_state)

def get_charger_state():
    """
    Reads the charger state.  Possible values::

        ChargerDisconnected = 0
        ChargerConnected = 1
        ChargerError = 2
        ChargingDone = 3

    :return: device charger state, one of :class:`MyMeSDK.constants.ChargerState`
    """
    _verify_initializing()
    return bt_manager.get_info_from_device(MyMeData.charger_state)

def get_device_time():
    """
    Reads the time of the connected device

    :return: 'datetime' object with the current device time,
    """
    _verify_initializing()
    return bt_manager.get_info_from_device(MyMeData.device_time)

def get_device_hardware_version():
    """
    Gets the device hardware version

    :return: Device hardwre version (string)
    """
    _verify_initializing()
    return bt_manager.get_device_hardware_version()

def get_device_software_version():
    """
    Gets the device software version

    :return: Device Software version (string)
    """
    _verify_initializing()
    return bt_manager.get_device_software_version()

def _request_full_image(frame_idx, full_image_cb):
    """

    :param: frame_idx: Index of frame for which to request a full image
    :param: full_image_cb: callback function to be called after full image
                          request is handled
    """
    _verify_initializing()
    bt_manager.request_full_image(frame_idx, full_image_cb)


# ******************* DATABASE INTERACTION FUNCTIONS ***********************
# Functions that send or request data from the SDK database
# **************************************************************************

def get_all_people():
    """
    Returns a list with all the people that exist in the database

    :return: list of :class:`MyMeSDK.myme_objects.MyMePerson` objects

    """
    _verify_initializing()
    return [db_person_to_myme_person(person) for person in
            db_manager.get_all_people()]


def set_name_to_person(my_me_person_id, name):
    """
    Sets the given name to given my_me_person_id

    :param: my_me_person_id: id of the :class:`MyMeSDK.myme_objects.MyMePerson` object
    :param: name: the name to set (string)
    :return: None
    """
    _verify_initializing()
    db_person = db_manager.get_person_by_person_id(my_me_person_id)
    if db_person is None:
         print_and_log('ERROR: person id {0} does not exist'.
                       format(my_me_person_id), ERROR)
         return
    db_person.name = name
    db_manager.commit_db()

# TODO - person - pass by id
def set_profile_picture(my_me_person_id, profile_pic):
    """
    Sets the given profile picture to the given my_me_person_id.

    :param: my_me_person_id: id of the :class:`MyMeSDK.myme_objects.MyMePerson` object
    :param: profile_pic: the prfoile picture to set as binary jpeg content
    :return: None
    """
    _verify_initializing()
    db_person = db_manager.get_person_by_person_id(my_me_person_id)
    db_person.profile_pic = profile_pic
    db_manager.commit_db()

def get_person(person_id):
    """
    Fetches a person by Id from the DB, with his list of faces

    :param: person_id: the person Id to fetch
    :return: :class:`MyMeSDK.myme_objects.MyMePerson` object or None if not found
    """
    _verify_initializing()
    return db_person_to_myme_person(
            (db_manager.get_person_by_person_id(person_id)))

def remove_person(person_id):
    """
    Removes the given person from the DB, any person's face(s) is(are) deleted as well

    :param: person_id to be removed
    :return: None
    """
    _verify_initializing()
    db_person = db_manager.get_person_by_person_id(person_id)
    if db_person is not None:
        db_manager.remove(db_person)

def reset_database():
    """
    Resets the entire database of the SDK. This deletes all people and faces stored!

    :return: None
    """
    _verify_initializing()
    db_manager._delete_db()

def associate_face(myme_face, myme_person):
    """
    Associates the given MyMeFace with the given MyMePerson
    Note the previous association of the given face is removed from the relevant person.

    :param: myme_face: the :class:`MyMeSDK.myme_objects.MyMeFace` to associate.
    :param: myme_person: the :class:`MyMeSDK.myme_objects.MyMePerson` to associate with.
    :return: None
    """
    _verify_initializing()
    db_person = db_manager.get_person_by_person_id(myme_person.id)
    if db_person is None:
        print_and_log('ERROR: person id {} does not exist'.
                      format(myme_person.id), ERROR)
        return
    db_face   = db_manager.get_face_by_face_id(myme_face.id)
    if db_face is None:
        print_and_log('ERROR: db face id {0} does not exist'.
                      format(myme_face.id), ERROR)
        return

    db_person.faces.append(db_face)
    db_manager.commit_db()

def delete_face(face_id):
    """
    Deletes the given face from the database.
    The reference to the face from the relevant person is also deleted

    :param: face_id: the face id to delete
    :return: None
    """
    _verify_initializing()
    db_face = db_manager.get_face_by_face_id(face_id)
    db_manager.remove(db_face)

def get_all_faces_from_time(start_time, end_time):
    """
    Returns all :class:`MyMeSDK.myme_objects.MyMeFace` detected between start_time and end_time.

    :param: start_time: state time (DateTime object)
    :param: end_time: end time (DateTime object)
    :return: list of  :class:`MyMeSDK.myme_objects.MyMeFace` matching the query
    """
    _verify_initializing()
    db_faces = db_manager.get_all_faces_from_time(start_time, end_time)
    return [db_face_to_myme_face(face) for face in db_faces]

def get_all_faces():
    """
    Returns a list of all :class:`MyMeSDK.myme_objects.MyMeFace` objects in the database

    :return: list of all :class:`MyMeSDK.myme_objects.MyMeFace` objects in the database
    """
    _verify_initializing()
    return [db_face_to_myme_face(face) for face in
            db_manager.get_all_faces()]

def request_image_for_face_id(face_id, face_image_cb):
    """
    Requests the image from the device that is associated with given id.

    :param: face_id: ID of the face in database
    :param: face_image_cb: Callback function that receives the fetched MyMeface (see example below).
    :return: None

    >>> def face_image_received_cb(myme_face):
    ...    if myme_face.face_image is not None:
    ...         myme_face.face_image.show(title='id: {}, timestamp: {}'''.format(myme_face.id, full_timestamp ))
    >>> api.request_image_for_face_id(id, face_image_received_cb)

    """
    _verify_initializing()
    db_face = db_manager.get_face_by_face_id(face_id)

    bt_manager.request_face_image(
            db_face_id=face_id,
            myme_face_id=db_face.myme_id,
            face_image_cb=face_image_cb)

def register_paired_device_state_updated_cb(cb):
    """
    Registers callback to be called whenever the paired device state is updated.

    :param: cb: callback function to be called with the device state (see example below)
    :return: None

    >>> def PairedDeviceStateUpdatedCb(new_device_state):
    ...     print "== device state updated to {0}".format(new_device_state)
    >>> api.register_paired_device_state_updated_cb(PairedDeviceStateUpdatedCb)

    """
    _verify_initializing()
    delegate.PairedDeviceStateUpdated = cb

def register_face_detected_cb(cb):
    """
    Registers a callback to be called whenever a face is detected.

    :param: cb: callback function to be called (see example below).
    :return: None

    >>> def FaceDetectedCb(face, person, probability, is_last_face_in_frame):
    ... # :param face: MyMeFace object holding the matched face does not include the actual image.
    ... # :param person: MyMePerson object corresponding to the matched person, or None if not found
    ... # :param probability: probability that <face> belongs to <person>
    ... # :param is_last_face_in_frame - whether this is the last face in this frame
    ...     print 'Face Detected! face.id: {}, detected at: {}, last in frame {}'.format(face.id, face.detected_time, is_last_face_in_frame)
    ...     if person is not None:
    ...         print 'Found matching Person! Person ID: {}, with {}% certainty.'.format(person.id, probability)
    >>> api.register_face_detected_cb(FaceDetectedCb)
    """
    _verify_initializing()
    delegate.FaceDetected = cb

def register_new_person_created_cb(cb):
    """
     Registers a callback to be called whenever a new person in created by the SDK.

    :param: cb: the callback to be called with the newly created person (see example below).
    :return: None

    >>> def NewPersonCreatedCb(person, timestamp):
    ...     print 'New person created with ID, number faces stored: {}'.format(person.id, len(person.faces)))
    >>> api.register_new_person_created_cb(NewPersonCreatedCb)
    """
    _verify_initializing()
    delegate.NewPersonCreated = cb

def _register_visual_topics_received_cb(cb):
    _verify_initializing()
    delegate.VisualTopicsReceived = cb

def register_ocr_line_found_cb(cb):
    """
    Registers a callback to be called whenever a new text line is found.
    The callback is triggered for each new line found. Once all lines at a specific time have been reported,
    the callback is called an additional time with [myme_ocr_line = None], to indicate this is the last line found
    at this given time.

    :param cb: the callback to be called (see example below).
    :return: None

    >>> def OcrLineFoundCb(myme_ocr_line, timestamp):
    ...     #Inovked when a line of text is detected in an image.
    ...     #param: myme_ocr_line: Line of text detected (OcrLine object)
    ...     #param: timestamp: Timestamp when line was detected
    ...     if myme_ocr_line is not None:
    ...         print "Line Detected: {}".format(myme_ocr_line.text.encode('utf-8'))
    ...     else:
    ...         print "end of OCR"
    >>> api.register_ocr_line_found_cb(OcrLineFoundCb)
    """
    _verify_initializing()
    delegate.OcrLineFound = cb

def register_device_tapped_cb(cb):
    """
    Registers a callback to be called whenever the device is tapped on.

    :param cb: The callback to be called.
    :return: None.

    >>> def DeviceTappedCb():
    ...     print "MyMe Was Tapped!"
    >>> api.register_device_tapped_cb(DeviceTappedCb)

    """
    _verify_initializing()
    delegate.DeviceTapped = cb

def register_barcode_detected_cb(cb):
    """
    Registers a callback to be called whenever a barcode has been detected.

    :param cb: the callback to be called.
            The callback is called with barcode type (string, one of EAN-13, UPC-A, EAN-8, UPC-E)
            and the barcode value itself (also a string)

    :return: None

    >>> def BarcodeDetectedCb(barcode_type, barcode_value, timestamp):
    ...     #param: barcode_type - string, one of EAN-13, UPC-A, EAN-8, UPC-E)
    ...     #param: barcode_value - string
    ...     #param: timestamp - detected time
    ...     print "barcode of type {} Detected: {}".format(barcode_type, barcode_value)
    >>> api.register_barcode_detected_cb(BarcodeDetectedCb)

    """
    _verify_initializing()
    delegate.BarcodeDetected = cb

def _stop():
    global is_stopped
    global _is_initialized
    if not is_stopped:
        # stop the bluetooth manager, this would also disconnect from device and stop bgapi lib
        bt_manager.stop()

        # stop the user callback thread
        user_callback_thread_stop_event.set()
        user_callback_thread.join()

        # stop the user callback thread
        face_session_mananger.stop()

        is_stopped = True
        _is_initialized=False

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