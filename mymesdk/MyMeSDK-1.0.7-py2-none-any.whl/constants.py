
from enum import Enum

SDK_APPNAME = 'myme_sdk'
SDK_VERSION = '0.1'
MYME_DB_NAME = 'myme_sdk.db'

class DeviceState(Enum):
    """Paired Device state"""

    NotFound = 1
    """Paired device not found"""

    Paired = 2
    """ Device paired but not connected """

    Connecting = 3
    """ Device is connecting """

    Connected = 4
    """ Device connected """

    LostConnection = 5
    """ Lost connection with Device, SDK Will attempt to reconnect """

    Shuttingdown = 6
    """ Device is about to turn off (e.g battery is close to 0%) or user requested shut down """

class ChargerState(Enum):
    """ Device Charger state"""

    ChargerDisconnected = 0
    """ Charger is disconencted """

    ChargerConnected = 1
    """ Charger is connected """

    ChargingDone = 2
    """ Chargering error has occurred """

    ChargerError = 3
    """ Charging done (battery is full) """

class BatteryState(Enum):
    """ State of the battery """

    BatteryFull = 0
    """ Battery is full """

    BatteryOK = 1
    """ Battery level within normal range """

    BatteryLow = 2
    """ Battery is low"""

    BatteryCritical = 3
    """ Battery level is critical, device about to shutdown"""

class ScanState(Enum):
    """ State of a scan for MyMe devices. see also :func:`MyMeSDK.api.scan_for_devices_with_timeout`"""

    FailedWithError = 0
    """ scanning failed State of scan for MyMe device"""

    SuccessDueToTimeout = 1
    """ scanning done """

class LightLevel(Enum):
    """ Detected Light Level """

    NoLight = 0
    """ No light detected """

    VeryLowLight = 1
    """ Very low light detected """

    LowLight = 2
    """ Low light detected """

    NormalLight = 3
    """ Normal light detected """

    HighLight = 4
    """ High light detected """

    VeryHighLight = 5
    """ Very high light detected """

class MyMeException(Exception):

    """ MyMeException - General error exception """

    pass

class MyMeConnectionError(Exception):
    """Connection Error Exception."""
    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.message)

    def __str__(self):
        return repr(self)


class ServiceUUID(Enum):
    FacesServiceUuid               		= "FB694B90-F49E-4597-8306-171BBA78F846"
    BatteryServiceUuid					= "0000180F-0000-1000-8000-00805F9B34FB"
    HardwareSoftwareServiceUuid			= "0000180A-0000-1000-8000-00805F9B34FB" #
    WordCloudServiceUuid				= "A8291D00-83C9-11E5-B96C-0002A5D5C51B"
    DebugServiceUuid					= "62967EA0-4F0C-11E5-AC7D-0002A5D5C51B"
    ChargerServiceUuid					= "FEC297BC-246B-4BF2-95BD-48353A86724D"
    TimeServiceUuid						= "C18094F9-2115-4371-AA97-123B881EE420"
    LowBatteryServiceUuid				= "37712D0D-ED77-4705-AFF3-B336F9EB87B9"
    GeneralInformationServiceUuid		= "2266F960-8847-4380-8566-7A3E7827FB91"
    TapServiceUuid						= "8D06CB14-BC4A-47EE-907F-2D3E814AEFF9"
    JpegServiceId                       = "152E2EC7-D5B9-4C96-B193-8760FA6B176E"
    GeneralDataService                  = "16c73ff5-51a8-4fd7-ab1b-adb05a3f9dde"


class MultiPacketNotifyCharactersticUUID(Enum):
    FaceImageCharacteristicUuid				= "EB6727C4-F184-497A-A656-76B0CDAC633A"
    FaceSignatureCharacteristicUuid         = "18F58CA0-44D0-11E5-9A12-0002A5D5C51B"
    ImangenetCharacteristicUuid             = "C58597C0-83C9-11E5-A0Cf-0002A5D5C51B"
    JpegCharacteristicUuid					= "8953B547-7AEC-4FA8-AC20-9F710D3FD856"
    OcrCharacteristicUuid					= "56BB0234-96E9-45DC-AC99-B2802AFF6289"


FACES_SERVICE_UUID                    = "FB694B90-F49E-4597-8306-171BBA78F846"
FACE_SIGNATURE_CHARACTERISTIC_UUID    = "18F58CA0-44D0-11E5-9A12-0002A5D5C51B"
FACE_IMAGE_CHARACTERISTIC_UUID        = "EB6727C4-F184-497A-A656-76B0CDAC633A"


HARDWARE_SOFTWARE_SERVICE_UUID        = "0000180A-0000-1000-8000-00805F9B34FB" #"180A"
BATTERY_LEVEL_SERVICE_UUID            = "0000180F-0000-1000-8000-00805F9B34FB" # "180F"
BATTERY_LEVEL_CHARACTERISTIC_UUID     = "00002A19-0000-1000-8000-00805F9B34FB" # "2A19"
HARDWARE_CHARACTERISTIC_UUID          = "00002A27-0000-1000-8000-00805F9B34FB" #"2A27"
SOFTWARE_CHARACTERISTIC_UUID          = "00002A28-0000-1000-8000-00805F9B34FB" #"2A28"


IMAGENET_SERVICE_UUID                 = "A8291D00-83C9-11E5-B96C-0002A5D5C51B"
IMAGENET_CHARACTERISTIC_UUID          = "C58597C0-83C9-11E5-A0Cf-0002A5D5C51B"

DEBUG_SERVICE_UUID                    = "62967EA0-4F0C-11E5-AC7D-0002A5D5C51B"
DEBUG_CHARACTERISTIC_UUID             = "E8775746-7836-4D91-8CAB-49FDAD594570"

CHARGER_SERVICE_UUID                  = "FEC297BC-246B-4BF2-95BD-48353A86724D"
CHARGER_CHARACTERISTIC_UUID           = "F2208A8F-A3C3-4B27-BF8F-513CC9FD6365"

TIME_SERVICE_UUID                     = "C18094F9-2115-4371-AA97-123B881EE420"
TIME_CHARACTERISTIC_UUID              = "E810CEA7-5FC3-4E3E-955D-00506117B4A2"

LOW_BATTERY_SERVICE_UUID              = "37712D0D-ED77-4705-AFF3-B336F9EB87B9"
LOW_BATTERY_CHARACTERISTIC_UUID       = "bb2ea6a9-a071-4253-b8b3-ec4c6bd4408d"

GENERAL_INFORMATION_SERVICE_UUID      = "2266F960-8847-4380-8566-7A3E7827FB91"
GENERAL_DEVICE_ID_CHARACTERISTIC_UUID = "5F34A16C-02D6-451A-BDAB-4330AFBA0264"

TAP_SERVICE_UUID                      = "8D06CB14-BC4A-47EE-907F-2D3E814AEFF9"
TAP_CHARACTERISTIC_UUID               = "E5FE7BBD-2C00-402A-B139-2769909BDA3A"

# NEW SERVICE! (Exclusive to Python SDK as of Now!!)
JPEG_SERVICE_UUID                     = "152E2EC7-D5B9-4C96-B193-8760FA6B176E"
JPEG_CHARACTERISTIC_UUID              = "8953B547-7AEC-4FA8-AC20-9F710D3FD856"

OCR_SERVICE_UUID                      = "CA644A25-FE7A-4329-90E3-B048AA5B11EE"
OCR_CHARACTERISTIC_UUID               = "56BB0234-96E9-45DC-AC99-B2802AFF6289"

BARCODE_SERVICE_UUID                  = "0D5C722F-8517-472C-B681-F67A36E36F27"
BARCODE_CHARACTERISTIC_UUID           = "99206FA0-0CAE-45D9-BBAD-70643FDBB77B"

GENERAL_DATA_SERVICE_UUID             = "16c73ff5-51a8-4fd7-ab1b-adb05a3f9dde"
LIGHT_LEVEL_CHARACTERISTIC_UUID       = "de5471f0-2877-470d-bc23-473759f805ad"