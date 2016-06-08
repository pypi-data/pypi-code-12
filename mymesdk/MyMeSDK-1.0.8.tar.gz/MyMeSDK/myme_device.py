
import threading
import traceback

from constants import *
from packet_parser import PacketParser
from utils.sdk_utils import print_and_log, ERROR, EXCEPTION

MyMeData = Enum('MyMeData',
                ['hw_version',
                 'sw_version',
                 'battery_state',
                 'battery_charge_level',
                 'charger_state',
                 'device_time',
                 'light_level'])


class MyMeDevice(object):
    """
    Class represents an instance of a MyMe device.
    """
    def __init__(self):
        self.handler = None
        self.device_state = None
        # Used to store last state in order to restore it after temporary state
        # change (ie when subscribing)
        self.last_device_state = None
        self.lock = threading.Lock()


        self.hw_version = None
        self.sw_version = None
        self.battery_state = None
        self.battery_charge_level = None
        self.charger_state = None
        self.device_time = None
        self.device_address = None
        self.light_level = None

    def fill_device_info(self, device_address):
        """
        Gets all the available device info upon connection and stores it in the
        object. This enables fast response for future user queries regarding
        device info.
        """
        if self.device_state != DeviceState.Connected:
            print_and_log('ERROR: Can\'t fill device info when not connected')

        with self.lock:
            self.device_address = device_address
            try:
                self.sw_version = PacketParser.parse_version_packet(
                    self.handler.char_read(SOFTWARE_CHARACTERISTIC_UUID))
                print_and_log('got device software_version: {}'
                              ''.format(self.sw_version))
            except Exception as ex:
                print_and_log(EXCEPTION, 'Error getting software vrsion from '
                              'MyMe device\nException Message: {}'.format(ex))

            try:
                self.hw_version = PacketParser.parse_version_packet(
                    self.handler.char_read(HARDWARE_CHARACTERISTIC_UUID))
                print_and_log('got device hardware_version: {}'
                              ''.format(self.hw_version))
            except Exception as ex:
                print_and_log(EXCEPTION, 'Error getting harwarde version from '
                              'MyMe Device\nException Message: {}'.format(ex))

            try:
                self.device_time =  PacketParser.parse_time_packet(
                    self.handler.char_read(TIME_CHARACTERISTIC_UUID))
                print_and_log('got device time: {}'
                              ''.format(self.device_time))
            except Exception as ex:
                print_and_log(EXCEPTION, 'Error getting device time from '
                              'MyMe Device\nException Message: {}'.format(ex))

            try:
                self.battery_charge_level = \
                    PacketParser.parse_battery_charge_level_packet(
                    self.handler.char_read(BATTERY_LEVEL_CHARACTERISTIC_UUID))
                print_and_log('got battery level: {}%'
                              ''.format(self.battery_charge_level))
            except Exception as ex:
                print_and_log(EXCEPTION, 'Error getting battery charge level'
                        'from MyMe Device\nException Message: {}'.format(ex))

            try:
                self.charger_state = PacketParser.parse_charger_packet(
                    self.handler.char_read(CHARGER_CHARACTERISTIC_UUID))
                print_and_log('got charger state: {}'
                              ''.format(self.charger_state))
            except Exception as ex:
                print_and_log(EXCEPTION, 'Error getting charger charge '
                        'from MyMe Device\nException Message: {}'.format(ex))

