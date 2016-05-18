
import abc
from constants import *

class MyMeDelegates():
    """
    This class provides an interface for the delegate functions that the SDK
    user may choose to implement. Any function that the user does not implement
    will have the default implementation defined here
    """
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        pass

    def ConnectedToDevice(self, device_address, error):
        """
        This deleagte is invoked after an attempt is made to connect to a MyMe
        device. On success, device_addr and device_name are the address/name
        of the MyMe device that user connected to. On failure, error contains
        the error message.
        :param device_addr: address of the device that user connected to
        :param error: on connection failure, contains error string
        """
        pass

    def ScanComplete(self, device_list, scan_result, error=None):
        """
        Called when a scan (following a call to scan_for_devices_with_timeout)
        is completed.
        :param device_list: List of devices.
        Each device is represented by dict with the following keys:
            "address" (device's MAC address)
            "name" (device name)
            "rssi" (signal strength)
        :param scan_result: scan compeltion reason (ScanState)
        :param error: in case of error, contains error message
        """
        pass

    def PairedDeviceStateUpdated(self, new_device_state):
        """
        This delegate is invoked when the MyMe device connection state changes
        :param state - The current device state
        """
        pass
    
    def FaceDetected(self, face, person, probability, is_last_face_in_frame):
        """
        This delegate is invoked when the MyMe device detects a face
        :param face: MyMeFace object holding the matched face does not include
                     the actual image nor image signature.
        :param person: MyMePerson object corresponding to the matched person
        :param probability: probability that <face> belongs to <person>
        :param is_last_face_in_frame: whether this is the last face for this franme
        """
        pass

    def NewPersonCreated(self, person, timestamp):
        """
        This delegate is invoked when the MyMe device detects multiple faces
        and recognizes all of them as the same person. The DB creates a new
        person with the faces.
        :param person: newly created person (MyMePerson object)
        :param timestamp: time when face was created (seconds from epoch float)
        """
        pass

    def VisualTopicsReceived(self, topics, timestamp):
        """
        This delegate is invoked when a new set of words is sent from the device.
        :param topics: list containing objects of type VisualTopic which
        contains topic and its probability of being in the frame. The list is
        sorted by probability.
        :param timestamp: the time that the words were sent from the device
        """
        pass

    def OcrLineFound(self, myme_ocr_line, timestamp):
        """
        Inovked when a line of text is detected in an image.
        :param myme_ocr_line: Line of text detected (OcrLine object).
                              None is sent in case this is the last line at this time
                              Note None might be sent even if no lines were sent, in case no
                              lines were deteceted at this time
        :param timestamp: Timestamp when line was detected
        """
        pass

    def BarcodeDetected(self, barcode_type, barcode_value, timestamp):
        """
        Invoked when a product barcode is detected in an image.
        :param barcode_type: The detected barcode type (ascii string)
        :param barcode_value: The detected barcode value (ascii string)
        :param timestamp: Time when barcode was detected
        """
        pass

    def ChargerStateUpdated(self, new_charger_state):
        """
        This delegate is invoked when the charger state is changed.
        :param new_charger_state: the state of the charger after the change
        """
        pass

    def LightLevelUpdated(self, new_light_level):
        """
        This delegate is invoked when the light level is changed
        :param new_light_level: the new light level detected
        """
        pass

    def DeviceTapped(self):
        """
        This delegate is called when the device is tapped
        """
        pass

    def BatteryStateUpdated(self, battery_state):
        """
        Called when the battery state is updated
        :param battery_state: BatteryState enum with the following options:
                            BatteryFull = 0
                            BatteryOK = 1
                            BatteryLow = 2
                            BatteryCritical = 3
        """
        pass


    def BatteryChargeLevelChanged(self, battery_level):
        """
        Called when the battery level is changed (expected to be called about
        once a minute while the device is connected)
        :param battery_level: Int from 1 to 100 (100 means charged 100%)
        """
        pass


    def QrCodeDetected(self, qr_code, timestamp):
        raise NotImplementedError
