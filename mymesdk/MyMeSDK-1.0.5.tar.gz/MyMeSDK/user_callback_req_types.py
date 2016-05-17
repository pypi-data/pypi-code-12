
import abc

from enum import Enum

class UserCallbackReqType(Enum):

    # These cb myme_requests call a delegate callback
    PairedDeviceStateUpdatedCbReq = 1
    FaceDetectedCbReq = 2
    NewPersonCreatedCbReq = 3
    VisualTopicsReceivedCbReq = 4
    OcrLineFoundCbReq = 5
    BarcodeDetectedCbReq = 6
    ChargerStateUpdatedCbReq = 7
    DeviceTappedCbReq = 8
    BatteryStateUpdatedCbReq = 9
    BatteryChargeLevelChangedCbReq = 10
    LightLevelUpdatedCbReq = 11

    # These myme_requests must get user_callback argument to call
    ScanCompleteCbReq = 12
    ConnectedToDeviceCbReq = 13
    FaceImageReceivedCbReq = 14
    FullImageReceivedCbReq = 15
    WriteToDebugCbReq = 16

class UserCallbackReq(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self.type = None

class PairedDeviceStateUpdatedCbReq(UserCallbackReq):
    def __init__(self, new_state):
        """
        This delegate is invoked when the MyMe device state changes
        :param new_state: - New device state
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.PairedDeviceStateUpdatedCbReq
        self.new_state = new_state


class FaceDetectedCbReq(UserCallbackReq):
    def __init__(self, face, person, probability, is_last_face_in_frame):
        """
        This delegate is invoked when the MyMe device detects a face
        :param face: MyMeFace object holding the matched face does not include
                     the actual image nor image signature.
        :param person: MyMePerson object corresponding to the matched person
        :param probability: probability that <face> belongs to <person>
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.FaceDetectedCbReq
        self.face=face
        self.person=person
        self.probability=probability
        self.is_last_face_in_frame=is_last_face_in_frame


class NewPersonCreatedCbReq(UserCallbackReq):
    def __init__(self, person, timestamp):
        """
        This delegate is invoked when the MyMe device detects multiple faces
        and recognizes all of them as the same person. The DB creates a new
        person with the faces.
        :param person: newly created person (MyMePerson object)
        :param timestamp: time when face was created (seconds from epoch float)
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.NewPersonCreatedCbReq
        self.person=person
        self.timestamp=timestamp


class VisualTopicsReceivedCbReq(UserCallbackReq):
    def __init__(self, topics, timestamp):
        """
        This delegate is invoked when a new set of words is sent from the device.
        :param topics: list containing objects of type VisualTopic which
        contains topic and its probability of being in the frame. The list is
        sorted by probability.
        :param timestamp: the time that the words were sent from the device
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.VisualTopicsReceivedCbReq
        self.topics=topics
        self.timestamp=timestamp


class OcrLineFoundCbReq(UserCallbackReq):
    def __init__(self,  myme_ocr_line, timestamp, is_frame_end=False):
        """
        Inovked when a line of text is detected in an image.
        :param myme_ocr_line: Line of text detected (OcrLine object)
        :param timestamp: Timestamp when line was detected
        :param is_frame_end: if true, this OCR packet is the last one
                             for the current frame
                            (packet may be empty or contain OCR line(s))
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.OcrLineFoundCbReq
        self.myme_ocr_line=myme_ocr_line
        self.timestamp=timestamp
        self.is_frame_end=is_frame_end


class BarcodeDetectedCbReq(UserCallbackReq):
    def __init__(self, barcode_type, barcode_value, timestamp):
        """
        Invoked when a product barcode is detected in an image.
        :param barcode: The detected barcode (ascii string)
        :param timestamp: Time when barcode was detected
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.BarcodeDetectedCbReq
        self.barcode_type = barcode_type
        self.barcode_value = barcode_value
        self.timestamp = timestamp


class ChargerStateUpdatedCbReq(UserCallbackReq):
    def __init__(self, new_charger_state):
        """
        This delegate is invoked when the charger state is changed.
        :param new_charger_state: the state of the charger after the change
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.ChargerStateUpdatedCbReq
        self.new_charger_state = new_charger_state

class LightLevelStateUpdatedCbReq(UserCallbackReq):
      def __init__(self, new_light_level):
        """
        This delegate is invoked when the light level is changed.
        :param new_light_level: the level of the light detected after the change
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.LightLevelUpdatedCbReq
        self.new_light_level = new_light_level

class DeviceTappedCbReq(UserCallbackReq):
    def __init__(self):
        """
        This delegate is called when the device is tapped
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.DeviceTappedCbReq


class BatteryStateUpdatedCbReq(UserCallbackReq):
    def __init__(self, battery_state):
        """
        Called when the battery state has been updated
        :param battery_state: BatteryState enum with the following options:
                            BatteryFull = 0
                            BatteryOK = 1
                            BatteryLow = 2
                            BatteryCritical = 3
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.BatteryStateUpdatedCbReq
        self.battery_state = battery_state


class BatteryChargeLevelChangedCbReq(UserCallbackReq):
    def __init__(self, battery_level):
        """
        Called when the battery level is changed (expected to be called about
        once a minute while the device is connected)
        :param battery_level: Int from 1 to 100 (100 means charged 100%)
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.BatteryChargeLevelChangedCbReq
        self.battery_level = battery_level


class ScanCompleteCbReq(UserCallbackReq):
    def __init__(self, sorted_device_list, scan_state, error, user_callback):
        """
        Called when a scan (following a call to scan_for_devices_with_timeout)
        is completed.
        :param sorted_device_list: List of devices.
        Each device is represented by dict with the following keys:
            "address" (device's MAC address)
            "name" (device name)
            "rssi" (signal strength)
        :param scan_state: scan compeltion reason (ScanState)
        :param error: in case of error, contains error message
        :param user_callback: User callback function to call
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.ScanCompleteCbReq
        self.sorted_device_list = sorted_device_list
        self.scan_state = scan_state
        self.error = error
        self.user_callback = user_callback


class ConnectedToDeviceCbReq(UserCallbackReq):
    def __init__(self, device_addr, error, user_callback):
        """
        Iinvoked after an attempt is made to connect to a MyMe
        device. On success, device_addr and device_name are the address/name
        of the MyMe device that user connected to. On failure, error contains
        the error message.
        :param device_addr: address of the device that user connected to
        :param error: on connection failure, contains error string
        :param user_callback: User callback function to call

        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.ConnectedToDeviceCbReq
        self.device_addr = device_addr
        self.error = error
        self.user_callback = user_callback


class FaceImageReceivedCbReq(UserCallbackReq):
    def __init__(self, myme_face, user_callback):
        """
        :param myme_face: MyMeFace object containing the received face image
        :param user_callback: User callback function to call
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.FaceImageReceivedCbReq
        self.myme_face = myme_face
        self.user_callback = user_callback


class FullImageReceivedCbReq(UserCallbackReq):
    def __init__(self, myme_image, user_callback):
        """
        :param MyMeImage object containing the received full image
        :param user_callback: User callback function to call
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.FullImageReceivedCbReq
        self.myme_image = myme_image
        self.user_callback = user_callback

class WriteToDebugCbReq(UserCallbackReq):
    def __init__(self, success, user_callback):
        """
        :param success: True if succeeded in writing message to MyMe device
        :param user_callback: User callback function to call
        :return:
        """
        UserCallbackReq.__init__(self)
        self.type = UserCallbackReqType.WriteToDebugCbReq
        self.success = success
        self.user_callback = user_callback