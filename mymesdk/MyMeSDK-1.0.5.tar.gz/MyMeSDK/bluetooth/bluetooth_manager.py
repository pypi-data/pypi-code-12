


import calendar
import datetime
import Queue
import signal
import struct
import sys
import threading
import time
import traceback

from collections import defaultdict

from packet_assembler import PacketAssembler
from ..myme_requests.request_types import *
from ..myme_objects import MyMeFace
from ..myme_device import MyMeDevice, MyMeData
from ..packet_parser import PacketParser
from ..pygatt.backends import BGAPIBackend
from ..pygatt.backends.bgapi import constants as bgapi_constants
from ..pygatt.exceptions import NotConnectedError
from ..pygatt.backends.bgapi.exceptions import ExpectedResponseTimeout
from ..pygatt.backends.bgapi.exceptions import BGAPIError
from ..utils.sdk_utils import (print_and_log, ERROR, EXCEPTION, INFO, int_to_bytes,
                               bytearray_to_image)


class BluetoothManager(threading.Thread):

    @staticmethod
    def _default_callback(self, *args, **kargs):
        pass

    SCAN_TIMEOUT = 5
    CONNECTION_TIMEOUT = 10
    MYME_DEVICE_NAME = 'MyMe'
    RETRY_CONNECT_SEC = 2

    def __init__(self,
                 sdk_charger_state_updated_cb,
                 sdk_device_tapped_cb,
                 sdk_battery_state_updated_cb,
                 sdk_battery_charge_level_updated_cb,
                 sdk_device_state_updated,
                 sdk_scan_complete_cb,
                 sdk_connected_to_device_cb,
                 sdk_face_signature_cb,
                 sdk_face_image_cb,
                 sdk_full_image_cb,
                 sdk_write_to_debug_cb,
                 sdk_visual_topics_cb,
                 sdk_ocr_line_cb,
                 sdk_barcode_cb,
                 sdk_light_level_cb):

        threading.Thread.__init__(self)
        # Program will exit if run_all_tests thread is terminated (ie: with ctrl+c)
        signal.signal(signal.SIGINT,self._sigint_handler)
        self.daemon = True
        self.req_queue = Queue.Queue()

        self.lock = threading.Lock()
        self.not_connecting_event = threading.Event()

        self.disconnect_requested = False
        self._stop_event = threading.Event()

        self.sdk_charger_state_updated_cb = sdk_charger_state_updated_cb
        self.sdk_device_tapped_cb = sdk_device_tapped_cb
        self.sdk_battery_state_updated_cb = sdk_battery_state_updated_cb
        self.sdk_battery_charge_level_updated_cb = sdk_battery_charge_level_updated_cb
        self.sdk_device_state_updated = sdk_device_state_updated
        self.sdk_scan_complete_cb = sdk_scan_complete_cb
        self.sdk_connected_to_device_cb = sdk_connected_to_device_cb
        self.sdk_face_signature_cb = sdk_face_signature_cb
        self.sdk_face_image_cb = sdk_face_image_cb
        self.sdk_full_image_cb = sdk_full_image_cb
        self.sdk_write_to_debug_cb = sdk_write_to_debug_cb
        self.sdk_visual_topics_cb = sdk_visual_topics_cb
        self.sdk_ocr_line_cb = sdk_ocr_line_cb
        self.sdk_barcode_cb = sdk_barcode_cb
        self.sdk_light_level_cb = sdk_light_level_cb

        while True:
            try:
                self.ble_adapter = BGAPIBackend()
                self.ble_adapter.start()
                break
            except ExpectedResponseTimeout as timeoutException:
                print_and_log('Try restarting the MyMe device and reinserting the '
                              'BLE dongle.')
                raise MyMeConnectionError(timeoutException.message)
            except BGAPIError as bgapi_error:
                print_and_log('BGAPIError {}'.format(bgapi_error.message), ERROR)
                raise MyMeException(bgapi_error.message)

        self.myme_device = MyMeDevice()
        self.myme_device.device_state = DeviceState.NotFound
        self.pending_requests = defaultdict(lambda : defaultdict(list))
        # Must update when connecting to device

        self.face_signature_assembler = PacketAssembler(self.face_signature_assembler_cb)
        self.face_image_assembler = PacketAssembler(self.face_image_assembler_cb)
        self.full_image_assembler = PacketAssembler(self.full_image_assembler_cb)
        self.imagenet_assembler = PacketAssembler(self.imagenet_assembler_cb)
        self.ocr_assembler = PacketAssembler(self.ocr_assembler_cb)
        self.barcode_assembler = PacketAssembler(self.barcode_assembler_cb)


    def _sigint_handler(self, signum, frame):
        print_and_log('CTRL-C pressed in bluetooth_manager thread. Will disconnect from device '
                  '(if connected), and exit.')
        self.stop()
        sys.exit(0)


    def run(self):
        while not self._stop_event.is_set():
            # Check connection status (if state is connected
            if self.myme_device.device_state == DeviceState.Connected:
                # get connection status and if disconnected, try reconnecting
                with self.lock:
                    try:
                        bgapi_device_status = \
                                self.myme_device.handler.get_connection_status()
                    except Exception as ex:
                        print_and_log('EXCEPTION trying to get connection status\n'
                                      'Exception message: {}'.format(ex))
                        continue

                if (bgapi_device_status ==
                    bgapi_constants.BGAPI_device_state.disconnected):
                    self.set_device_state(DeviceState.LostConnection)
                    print_and_log('NOTE: LOST CONNECTION TO DEVICE\n', ERROR)

            if self.myme_device.device_state == DeviceState.LostConnection:
                print_and_log('Attempting to reconnect to device after losing '
                              'connection.\n', ERROR)
                try:
                    self.ble_adapter.stop()
                    self.ble_adapter = BGAPIBackend()
                    self.ble_adapter.start()
                except Exception as ex:
                    print_and_log('EXCEPTION resetting the BGAPIBackend\n'
                                  'Exception Message: {}'.format(ex))
                req = ConnectionRequest(
                                timeout_sec=4,
                                device_addr=self.myme_device.device_address,
                                callback=None, event=threading.Event())
                with self.lock:
                    self._handle_connection_request(req)
                if req.success:
                    print_and_log('Successfully reconnected to device.')
                else:
                    print_and_log('Reconnect failed.', ERROR)
                    time.sleep(2)
                    continue

            try:
                item = self.req_queue.get(timeout=2)
                with self.lock:
                    self._handle_item(item)
                self.req_queue.task_done()

            except Queue.Empty: # timeout
                continue

        # upon exit, disconnect from device if we are connected
        if self.myme_device.device_state is DeviceState.Connected:
            self.disconnect_from_device()

        self.ble_adapter.stop()


    def stop(self):
        """
        Disconnects from device (if connected) and terminates the thread by exiting
        :return:
        """
        self._stop_event.set()

    def get_characterstics_list(self):
        if self.myme_device.device_state is not DeviceState.Connected:
            error = 'NOTE: Requested to get characterstic list while not connected.'
            print_and_log(error)
            return

        char_list = self.myme_device.handler.discover_characteristics()
        for char_uuid_str, char_obj in char_list.iteritems():
            print_and_log("Characteristic 0x{} is handle 0x{}"
                          "".format(char_uuid_str, char_obj.handle))

            for desc_uuid_str, desc_handle in char_obj.descriptors.iteritems():
                print_and_log("Characteristic descriptor 0x{} is handle 0x{}"
                              "".format(desc_uuid_str, desc_handle))

    def get_info_from_device(self, data_member):
        """
        General function which returns data from a connected MyMeDevice
        :param name of data_member to get from device
        :return: On success returns requested data
        """
        if (self.myme_device.device_state !=  DeviceState.Connected):
            print_and_log('ERROR: Cannot get {} - not connected to device.'
                          ''.format(data_member), ERROR)
            #raise MyMeConnectionError('ERROR: Cannot get data while not connected to device.')
            return None

        try:
            if data_member == MyMeData.sw_version:
                return self.myme_device.sw_version
            elif data_member == MyMeData.hw_version:
                return self.myme_device.hw_version
            elif data_member == MyMeData.battery_charge_level:
                return self.get_battery_charge_level()
            elif data_member == MyMeData.battery_state:
                return self.get_battery_state()
            elif data_member == MyMeData.charger_state:
                return self.get_charger_state()
            elif data_member == MyMeData.device_time:
                return  self.get_device_time()
            elif data_member == MyMeData.light_level:
                return self.get_light_level()
        except Exception as ex:
            print_and_log('ERROR getting data member: {} from device.\n'
                          'Exception Message: {}'.format(data_member, ex))
            return None

    def get_device_time(self):
        with self.lock:
            device_time = self.myme_device.handler.char_read(TIME_CHARACTERISTIC_UUID)
            self.myme_device.device_time = PacketParser.parse_time_packet(device_time)
            return self.myme_device.device_time

    def get_battery_charge_level(self):
        """
        Gets the percent charge [0, 1] of the battery from the device
        Device returns battery level in the following format:
            1 byte - battery level from 0 to 100 percent (unsigned 8 bit)
        :param battery_charge_level_cb: callback function
        """
        with self.lock:
            battery_charge_level = self.myme_device.handler.char_read(
                    BATTERY_LEVEL_CHARACTERISTIC_UUID)
            self.myme_device.battery_charge_level = PacketParser.parse_battery_charge_level_packet(battery_charge_level)
            return self.myme_device.battery_charge_level

    def get_battery_state(self):
        """
        Get the BatteryState of the device battery. The possible values are:
                BatteryOK = 0
                BatteryCharging = 1
                BatteryLow = 2
                BatteryCritical = 3 # Device will shutdown upon reaching state
        :param battery_state_cb: callback function
        """
        with self.lock: # note this is the caller context -  make sure the run_all_tests thread is not accessing now the bgapi
            battery_state = self.myme_device.handler.char_read(LOW_BATTERY_CHARACTERISTIC_UUID)
            self.myme_device.battery_state = PacketParser.parse_battery_state_packet(battery_state)
            return self.myme_device.battery_state

    def get_charger_state(self):
        with self.lock:
            charger_status = self.myme_device.handler.char_read(
                    CHARGER_CHARACTERISTIC_UUID)
            self.myme_device.charger_state = PacketParser.parse_charger_packet(charger_status)
            return self.myme_device.charger_state

    def get_light_level(self):
        with self.lock:
            light_level = self.myme_device.handler.char_read(LIGHT_LEVEL_CHARACTERISTIC_UUID)
            self.myme_device.light_level = PacketParser.parse_light_level_packet(light_level)
            return self.myme_device.light_level

    def get_device_state(self):
        return self.myme_device.device_state

    def set_device_state(self, new_state):
        self.last_device_state = self.myme_device.device_state
        self.myme_device.device_state = new_state
        self.sdk_device_state_updated(new_state)

    def get_device_hardware_version(self):
        return self.myme_device.hw_version

    def get_device_software_version(self):
        return self.myme_device.sw_version


    def connect_to_paired_device_with_timeout(self, timeout_secs, device_addr,
                                            callback=None, block=False):
        """
        Connects to a myme device at <device_addr>. In case of failure, will
        retry until success.

        :param timeout_secs:
        :param device_addr:
        :param callback:
        :param block: if True, function will block until the connection request
                      is handled by the request handling Thread
        :return: (True, None) on success or (False, <error msg>) on failure
        """
        if (timeout_secs <= 0):
            timeout_secs = self.CONNECTION_TIMEOUT

        connect_req = ConnectionRequest(timeout_secs, device_addr, callback,
                                        threading.Event())
        self.req_queue.put(connect_req)

        if block:
            while (not connect_req.event.is_set() and
                  not self._stop_event.is_set()):
                connect_req.event.wait(0.5)

        if connect_req.success == True:
            error = None
        else:
            error = ("ERROR trying to connect to MyMe device at address: {}"
                    "".format(device_addr))

        return connect_req.success, error


    def disconnect_from_device(self):

        if (self.myme_device.device_state not in
                [ DeviceState.Connected, DeviceState.LostConnection] ) :
            error = 'NOTE: Requested to disconnect while not connected.'
            print_and_log(error)
            return False


        self.disconnect_requested = True

        # Wait for reconnect loop to stop and release the lock
        if not self.not_connecting_event.is_set():
            print 'waiting for not_connecting_event to be set'
            while (not self.not_connecting_event.event.is_set() and
                   not self._stop_event.is_set()):
                self.not_connecting_event.wait()

        try:
            self.ble_adapter.stop()
            self.ble_adapter = BGAPIBackend()
            self.ble_adapter.start()
        except Exception as ex:
            print_and_log('EXCEPTION trying to disconnect from MyMe device.\n'
                          'Exception Message: {}'.format(ex))

        #self.myme_device.handler.disconnect()
        self.set_device_state(DeviceState.Paired)

        self.disconnect_requested = False
        return True

    def scan_for_peripherals_with_timeout(self, timeout):
        """
        """
        if (timeout <= 0):
            timeout = self.SCAN_TIMEOUT

        scan_req = ScanRequest(timeout)
        scan_req.event = threading.Event()
        self.req_queue.put(scan_req)

        # wait for completion

        while (not scan_req.event.is_set() and not self._stop_event.is_set()):
            scan_req.event.wait(0.5)

        # return result
        return scan_req.sorted_device_list, scan_req.scan_state, scan_req.error


    def write_to_debug(self, text, debug_cb=None):
        """
        Outputs <text> to the device stdin
        :param text: text to write
        :param debug_cb: optional user callback which reports whether the request
                        to write to MyMe was successful
        """
        self.req_queue.put(WriteToDebugRequest(text, debug_cb))


    def request_face_image(self, db_face_id, myme_face_id, face_image_cb=None):
        """
        Sends a request to a MyMe device to fetch a face image for <db_face_id>
        :param db_face_id: Id of the face in the Faces DB
        :param myme_face_id: MyMe application internal id of the face for which
                             to fetch an image
        :param face_image_cb: callback function
        """
        self.req_queue.put(FaceImageRequest(db_face_id=db_face_id,
                                            myme_face_id=myme_face_id,
                                            callback=face_image_cb))

    def request_full_image(self, frame_idx, full_image_cb=None):
        """
        Sends a request to a MyMe device to fetch a full image for <frame_idx>
        :param frame_idx: Index of frame for which user wants to fetch an image
        :param full_image_cb: callback function to be called after full image
                              request is handled
        """
        self.req_queue.put(FullImageRequest(frame_idx, full_image_cb))

    # ************************** PRIVATE FUNCTIONS *****************************

    def _subscribe_to_all_services(self):
        """
        Subsribes to all avilable services on a MyMe device
        :param callback_dict: dict mapping ServiceName to callback
        function for that service. For each service that has a matching callback
        function, that function will be called on any notification from the service
        """
        self.myme_device.handler.subscribe(FACE_IMAGE_CHARACTERISTIC_UUID,
                                    self.FaceImageCallback)
        self.myme_device.handler.subscribe(IMAGENET_CHARACTERISTIC_UUID,
                                           self.ImagenetCallback, indication=True)
        self.myme_device.handler.subscribe(JPEG_CHARACTERISTIC_UUID,
                                    self.FullImageCallback)
        self.myme_device.handler.subscribe(BATTERY_LEVEL_CHARACTERISTIC_UUID,
                                           self.battery_level_cb)
        self.myme_device.handler.subscribe(LOW_BATTERY_CHARACTERISTIC_UUID,
                                           self.low_battery_cb)
        self.myme_device.handler.subscribe(CHARGER_CHARACTERISTIC_UUID,
                                           self.charger_cb)
        self.myme_device.handler.subscribe(OCR_CHARACTERISTIC_UUID,
                                    self.OcrCallback, indication=True)
        self.myme_device.handler.subscribe(TAP_CHARACTERISTIC_UUID,
                                           self.tap_cb, indication=True)
        self.myme_device.handler.subscribe(BARCODE_CHARACTERISTIC_UUID,
                                    self.BarcodeCallback, indication=True)
        self.myme_device.handler.subscribe(FACE_SIGNATURE_CHARACTERISTIC_UUID,
                                    self.FaceSignatureCallback, indication=True)
        self.myme_device.handler.subscribe(LIGHT_LEVEL_CHARACTERISTIC_UUID,
                                           self.light_level_callback, indication=True)


    def _subscribe_to_service(self, service_uuid, callback=None):
        """
        :param service_uuid: uuid of service to subscribe to
        :param callback: optional callback function for device to call upon
                         notification from service
        """
        if (self.myme_device.device_state not in
                [DeviceState.Connected]):
            if callback:
                error=('ERROR: Cannot subscribe to services - device'
                       'is in an incorrect state ({})'
                       ''.format(self.myme_device.device_state))
                callback(error=error)
            return

        self.set_device_state(DeviceState.Subscribing)
        self.myme_device.handler.subscribe(service_uuid, callback)
        self.set_device_state(self.myme_device.last_device_state)


    # **************************************************************************
    # *********************** USER REQUEST HANDLERS ****************************
    # **************************************************************************


    def _handle_scan_request(self, req):
        device_list = []
        error = None
        try:
            device_list = self.ble_adapter.filtered_scan(
                    self.MYME_DEVICE_NAME, req.request_timeout)
            scan_state = ScanState.SuccessDueToTimeout
        except Exception as ex:
            message = ('EXCEPTION when running _handle_scan_request\n'
                       'Exception Message: {}'.format(ex))
            traceback.print_exc()
            print_and_log(message, EXCEPTION)
            error =  message
            scan_state = ScanState.FailedWithError

        # sort by descending RSSI order
        for device in device_list:
            device['rssi'] = int(device['rssi'])

        sorted_list = sorted(device_list, key=lambda k: k['rssi'], reverse=True)

        req.sorted_device_list = sorted_list
        req.scan_state = scan_state
        req.error = error

        # done, signal the caller in case it is blocked
        req.event.set()

    def _handle_connection_request(self, req):
        if (self.myme_device.device_state not in
            [DeviceState.Paired, DeviceState.LostConnection]):
            req.error=('Cannot connect to device because device is in an incorrect '
                   'state: {}. (Must be in Paired to connect'
                   ''.format(self.myme_device.device_state))
            req.success = False
            self.sdk_connected_to_device_cb(None, req.error, req.callback)
            req.event.set()
            self.not_connecting_event.set()
            return

        while not req.success:
            if self.disconnect_requested:
                req.error = ('Aborting connection attempt since user '
                             'requested to disconnect.')
                req.success = False
                self.sdk_connected_to_device_cb(None, req.error, req.callback)
                req.event.set()
                self.not_connecting_event.set()
                return

            self.not_connecting_event.clear()

            try:
                self.set_device_state(DeviceState.Connecting)
                self.myme_device.handler = self.ble_adapter.connect(
                    address=req.device_addr,
                    addr_type=bgapi_constants.ble_address_type['gap_address_type_random'],
                    timeout=req.request_timeout)
                self._subscribe_to_all_services()
                req.success = True
                self.set_device_state(DeviceState.Connected)

            except Exception as ex:
                print_and_log('EXCEPTION when trying to connect to device, '
                              'will retry in 2 seconds.\nException Message: {}'
                              ''.format(ex))
                self.set_device_state(self.last_device_state)
                req.success = False
                req.error = \
                    ('Failure when trying to connect to device at address: '
                     '{}\nException Message: {}\nRETRYING in {} seconds.'
                     ''.format(req.device_addr, ex, self.RETRY_CONNECT_SEC))
                try:
                    self.ble_adapter.disconnect_all()
                    self.sdk_connected_to_device_cb(None, req.error, req.callback)
                except Exception as ex:
                    pass
                time.sleep(1)


        try:
            self.get_characterstics_list()
            self.myme_device.fill_device_info(req.device_addr)
            self._set_device_time_if_needed(self.myme_device.device_time)
            #self.sdk_connected_to_device_cb(req.device_addr, None, req.callback)
        except Exception as ex:
            print_and_log('EXCEPTION message: {}'.format(ex))


        self.not_connecting_event.set()
        req.event.set()


    def _set_device_time_if_needed(self, device_time):

        now = datetime.datetime.now()
        # if device time is different than system time by more than 20 seconds, set it
        if (abs((now -  device_time).total_seconds()) > 20):
            print_and_log("Device time ({}) differs from system time ({}) by"
                          " more than 20 seconds. Setting time on device to "
                          "system time".format(device_time, now), INFO)
            # get timestamp
            now_timestamp = calendar.timegm(now.timetuple())
            # and set to device
            self._set_device_time(now_timestamp)

    def _set_device_time(self, time_to_set):
        # conver int to little endian bytearray
        hex_packet = bytearray(struct.pack("<I", time_to_set))
        try:
            self.myme_device.handler.char_write(TIME_CHARACTERISTIC_UUID,
                                                    hex_packet)

        except Exception as ex:
            print_and_log('ERROR: Failed trying to set device time.\n'
                          'Exception Message: {}'.format(ex), ERROR)



    def _handle_write_to_debug_request(self, req):
        if (self.myme_device.device_state not in
                [DeviceState.Connected]):
            print_and_log('ERROR: cannot carry out write to debug request: '
                               'Not connected to device.', ERROR)
            return

        hex_packet = bytearray(req.text)
        try:
            self.myme_device.handler.char_write(DEBUG_CHARACTERISTIC_UUID,
                                                hex_packet)
            self.sdk_write_to_debug_cb(True, req.cb)
        except Exception as ex:
            print_and_log('ERROR: Failed trying to write to debug.\n'
                          'Exception Message: {}'.format(ex), ERROR)
            self.sdk_write_to_debug_cb(False, req.cb)

    def _handle_get_face_image_request(self, req):
        if (self.myme_device.device_state not in
                [DeviceState.Connected]):
            print_and_log('ERROR: cannot carry out request face image request: '
                               'Not connected to device.', ERROR)
            return
        try:
            header = bytearray([0x00])
            face_id = bytearray(int_to_bytes(req.myme_face_id, length=4))
            timestamp = bytearray([0x00 for i in range(4)])
            hex_packet = header + face_id + timestamp
            self.pending_requests[RequestType.FaceImageRequest][req.myme_face_id].append(req)
            self.myme_device.handler.char_write(FACE_IMAGE_CHARACTERISTIC_UUID,
                                                hex_packet)
        except Exception as ex:
            print_and_log('EXCEPTION when trying to request face image id: {}\n'
                          'Exception Message: {}'.format(req.myme_face_id, ex),
                          EXCEPTION)


    def _handle_get_face_full_image_request(self, req):
        if (self.myme_device.device_state not in
                [DeviceState.Connected]):
             print_and_log('ERROR: cannot carry out request face image request: '
                               'Not connected to device.', ERROR)
        try:
            header = bytearray([0x00])
            frame_idx = bytearray(int_to_bytes(req.frame_idx, length=4))
            timestamp = bytearray([0x00 for i in range(4)])
            hex_packet = header + frame_idx + timestamp
            self.pending_requests[RequestType.FullImageRequest][req.frame_idx].append(req)
            self.myme_device.handler.char_write(JPEG_CHARACTERISTIC_UUID,
                                                hex_packet)
        except NotConnectedError:
            print_and_log('ERROR: tried writing to face_image characteristic '
                               'while not connected.', ERROR)

    # **************************************************************************
    # ********************* ASSEMBLER RESPONSE HANDLERS ************************
    # **************************************************************************

    def _handle_face_signature_assembler_response(self, res):
        try:
            face_id, timestamp, signature_int_array, flag = \
                           PacketParser.parse_face_signature_packet(res.packet)
            self.sdk_face_signature_cb(face_id, timestamp, signature_int_array, flag)
        except Exception as ex:
            print_and_log('EXCEPTION handling face signature assembler response'
                          '\nException Message: {}'.format(ex))

    def _handle_face_image_assembler_response(self, res):
        try:
            myme_face_id, detected_time, raw_image_bytearray = \
                PacketParser.parse_face_image_packet(res.packet)
        except Exception as ex:
            print_and_log('EXCEPTION parsing received face image.\n'
                          'Exception Message: {}'.format(ex))
            return


        curr_req_list = \
            self.pending_requests[RequestType.FaceImageRequest].get(myme_face_id)
        for req in curr_req_list:
            self.sdk_face_image_cb(req.db_face_id, detected_time,
                                   raw_image_bytearray, req.callback)


    def _handle_full_image_assembler_response(self, res):
        try:
            myme_image = PacketParser.parse_full_image_packet(res.packet)
        except Exception as ex:
            print_and_log('EXCEPTION parsing received full image.\n'
                          'Exception Message: {}'.format(ex))
            return

        curr_req_list = \
            self.pending_requests[RequestType.FullImageRequest].get(myme_image.frame_idx)
        for req in curr_req_list:
            self.sdk_full_image_cb(myme_image, res.callback)

    def _handle_imagenet_assembler_response(self, res):
        try:
            visual_topics_list, timestamp = \
                PacketParser.parse_imagenet_packet(res.packet)
            self.sdk_visual_topics_cb(visual_topics_list, timestamp)
        except Exception as ex:
            print_and_log('EXCEPTION parsing received visual topcics\n'
                          'Exception Message: {}'.format(ex))

    def _handle_ocr_assembler_response(self, res):
        try:
            ocr_lines_list, timestamp, is_frame_end = \
                PacketParser.parse_ocr_packet(res.packet)
        except Exception as ex:
            print_and_log('EXCEPTION parsing received OCR lines\n'
                          'Exception Message: {}'.format(ex))
            return

        for line in ocr_lines_list:
            self.sdk_ocr_line_cb(line, timestamp)
        # if is_frame_end is true, call the callback with ocr_line = None
        if is_frame_end:
            self.sdk_ocr_line_cb(None, timestamp, is_frame_end)

    def _handle_item(self, req):
        try:
            if req.request_type == RequestType.ScanRequest:
                self._handle_scan_request(req)
            elif req.request_type == RequestType.ConnectionRequest:
                self._handle_connection_request(req)
            elif req.request_type == RequestType.WriteToDebugRequest:
                self._handle_write_to_debug_request(req)
            elif req.request_type == RequestType.FaceImageRequest:
                self._handle_get_face_image_request(req)
            elif req.request_type == RequestType.FullImageRequest:
                self._handle_get_face_full_image_request(req)
            elif req.request_type == RequestType.FaceSignatureAssemblerResponse:
                self._handle_face_signature_assembler_response(req)
            elif req.request_type == RequestType.FaceImageAssemblerResponse:
                self._handle_face_image_assembler_response(req)
            elif req.request_type == RequestType.FullImageAssemblerResponse:
                self._handle_full_image_assembler_response(req)
            elif req.request_type == RequestType.ImagenetAssemblerResponse:
                self._handle_imagenet_assembler_response(req)
            elif req.request_type == RequestType.OcrAssemblerResponse:
                self._handle_ocr_assembler_response(req)
            else:
                print_and_log('ERROR: got unsupported request of type - {}. '
                              'Ignoring.'.format(req.request_type),ERROR)
        except Exception as ex:
            print_and_log('Exception handling request of type: {}'
                          ''.format(req.request_type))

    # ***************** BGAPIE RECEIVER THREAD CALLBACKS ***********************
    # Set of callbacks for bgapi receiver thread to call upon receiving a
    # notification from a characteristic
    # **************************************************************************

    def FaceSignatureCallback(self, handle, packet):
        self.face_signature_assembler.send(packet)

    def FaceImageCallback(self, handle, packet):
        self.face_image_assembler.send(packet)

    def ImagenetCallback(self, handle, packet):
        self.imagenet_assembler.send(packet)

    def FullImageCallback(self, handle, packet):
        self.full_image_assembler.send(packet)

    def OcrCallback(self, handle, packet):
        self.ocr_assembler.send(packet)

    def BarcodeCallback(self, handle, packet):
        self.barcode_assembler.send(packet)

    # ************************** ASSEMBLER CALLBACKS ***************************
    # Set of default callbacks for the assembler to call upon receiving a complete packet
    # Each request may override the default callback with one specific to the request
    # **************************************************************************

    def face_signature_assembler_cb(self, face_sig_packet):
        face_assembler_res = FaceSignatureAssemblerResponse(face_sig_packet)
        self.req_queue.put(face_assembler_res)

    def face_image_assembler_cb(self, face_image_packet):
        face_image_res = FaceImageAssemblerResponse(face_image_packet)
        self.req_queue.put(face_image_res)

    def full_image_assembler_cb(self, full_image_packet):
        full_image_res = FullImageAssemblerResponse(full_image_packet)
        self.req_queue.put(full_image_res)

    def imagenet_assembler_cb(self, visual_topics_packet):
        imagenet_assembler_res = ImagenetAssemblerResponse(visual_topics_packet)
        self.req_queue.put(imagenet_assembler_res)

    def ocr_assembler_cb(self, packet):
        ocr_assembler_res = OcrAssemblerResponse(packet)
        self.req_queue.put(ocr_assembler_res)

    def charger_cb(self, handle, packet):
        new_charger_state = PacketParser.parse_charger_packet(packet)
        if (new_charger_state is not None):
            self.sdk_charger_state_updated_cb(new_charger_state)

    def tap_cb(self, handle, packet):
        self.sdk_device_tapped_cb()

    def light_level_callback(self, handle, packet):
        new_light_level_state = PacketParser.parse_light_level_packet(packet)
        if new_light_level_state is not None:
            self.sdk_light_level_cb(new_light_level_state)

    def low_battery_cb(self, handle, packet):
        new_battery_state = PacketParser.parse_battery_state_packet(packet)
        if new_battery_state is not None:
            self.sdk_battery_state_updated_cb(new_battery_state)

    def battery_level_cb(self, handle, packet):
        battery_level = PacketParser.parse_battery_charge_level_packet(packet)
        if battery_level is not None:
            self.sdk_battery_charge_level_updated_cb(battery_level)

    def barcode_assembler_cb(self, packet):
        (barcode_type, barcode_value, timestamp) = PacketParser.parse_barcode_packet(packet)
        self.sdk_barcode_cb(barcode_type, barcode_value, timestamp)


