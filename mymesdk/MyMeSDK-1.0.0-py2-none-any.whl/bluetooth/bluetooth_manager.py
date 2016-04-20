import threading
import time
import traceback
import Queue
from collections import defaultdict

from packet_assembler import PacketAssembler
from ..request_types import *
from ..myme_data_objects import MyMeFace
from ..myme_device import MyMeDevice, MyMeData
from ..packet_parser import PacketParser
from ..pygatt.backends import BGAPIBackend
from ..pygatt.backends.bgapi import constants
from ..pygatt.exceptions import NotConnectedError
from ..utils.sdk_utils import (print_and_log, ERROR, EXCEPTION, int_to_bytes,
                               bytearray_to_image)


class BluetoothManager(threading.Thread):

    @staticmethod
    def _default_callback(self, *args, **kargs):
        pass

    SCAN_TIMEOUT = 5
    CONNECTION_TIMEOUT = 10
    MYME_DEVICE_NAME = 'MyMe'
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
                 sdk_barcode_cb):

        threading.Thread.__init__(self)
        # Program will exit if run_all_tests thread is terminated (ie: with ctrl+c)
        self.daemon = True
        self.req_queue = Queue.Queue()
        self.lock = threading.Lock()
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

        while True:
            try:
                self.ble_adapter = BGAPIBackend()
                self.ble_adapter.start()
                break
            except Exception as ex:
                print_and_log('Exception when starting BLE BGAPI Backend.\n'
                              'Exception Message: {}'.format(ex))
                print_and_log('Try restarting the MyMe device and reinserting the '
                              'BLE dongle. Will retry in 5 seconds.')
                time.sleep(5)

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


    # TODO - add_and_commit stop ability
    # TODO reconnect upon disconnection


    def run(self):
        while not self._stop_event.is_set():
            try:
                item = self.req_queue.get(2)
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
        self.join()

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

    def get_info_from_device(self, data_member, callback):
        """
        General function which returns data from a connected MyMeDevice
        :param name of data_member to get from device
        :return: On success returns requested data
        """
        if (self.myme_device.device_state not in
                [DeviceState.Connected, DeviceState.Subscribing]):
            callback(error='ERROR: Cannot get {} - not connected to device.'.format(data_member))
            return

        if data_member == MyMeData.sw_version:
            return self.myme_device.sw_version
        elif data_member == MyMeData.hw_version:
            return self.myme_device.hw_version
        elif data_member == MyMeData.battery_charge_level:
            self.get_battery_charge_level(callback)
        elif data_member == MyMeData.battery_state:
            self.get_battery_state(callback)
        elif data_member == MyMeData.charger_state:
            self.get_charger_state(callback)
        elif data_member == MyMeData.device_time:
            self.get_device_time(callback)

    def get_device_time(self, time_callback):
        with self.lock:
            device_time = self.myme_device.handler.char_read(TIME_SERVICE_UUID)
            # TODO - parse return value
            self.myme_device.device_time = device_time
            time_callback(device_time)

    def get_battery_charge_level(self, battery_charge_level_cb):
        """
        Gets the percent charge [0, 1] of the battery from the device
        Device returns battery level in the following format:
            1 byte - battery level from 0 to 100 percent (unsigned 8 bit)
        :param battery_charge_level_cb: callback function
        """
        with self.lock:
            battery_charge_level = self.myme_device.handler.char_read(
                    BATTERY_LEVEL_CHARACTERISTIC_UUID)
            # TODO - parse return value
            self.myme_device.battery_charget_level = battery_charge_level
            if battery_charge_level_cb is not None:
                battery_charge_level_cb(battery_charge_level)

    def get_battery_state(self, battery_state_cb):
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
            # TODO - parse return value
            self.myme_device.battery_state = battery_state
            battery_state_cb(battery_state)


    def get_charger_state(self, charger_state_cb):
        with self.lock:
            charger_status = self.myme_device.handler.char_read(
                    CHARGER_CHARACTERISTIC_UUID)
            # TODO - parse return value
            self.myme_device.charger_state = charger_status
            charger_state_cb(charger_status)

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
                                              callback=None, block=False, tries=1):
        """

        :param timeout_secs:
        :param device_addr:
        :param callback:
        :param block: if True, function will block until the connection request
                      is handled by the request handling Thread
        :param tries: Number of times to try connecting in case of failure
                     (will only retry if <block> is True) If tries is < 1,
                     will retry infinitely
        :return:
        """
        if (timeout_secs <= 0):
            timeout_secs = self.CONNECTION_TIMEOUT

        connect_req = ConnectionRequest(timeout_secs, device_addr, callback)
        connect_req.event = threading.Event()
        self.req_queue.put(connect_req)

        if block:
            if tries < 1:
                tries = int(1e18)
            while tries:
                connect_req.event.wait()
                if connect_req.success == True:
                    return
                tries -= 1


    def disconnect_from_device(self, callback=None):
        if self.myme_device.device_state is not DeviceState.Connected:
            error = 'NOTE: Requested to disconnect while not connected.'
            print_and_log(error)
            if callback:
                callback(False, error=error)
            return

        self.myme_device.handler.disconnect()
        self.set_device_state(DeviceState.Paired)
        if callback:
            callback(True)

    def scan_for_peripherals_with_timeout(self, timeout, block= False, scan_cb=None):
        """
        """
        if (timeout <= 0):
            timeout = self.SCAN_TIMEOUT

        scan_req = ScanRequest(timeout, scan_cb)
        scan_req.event = threading.Event()
        self.req_queue.put(scan_req)
        if block:
            scan_req.event.wait()

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
        self.myme_device.handler.subscribe(FACE_SIGNATURE_CHARACTERISTIC_UUID,
                                    self.FaceSignatureCallback, indication=True)
        self.myme_device.handler.subscribe(IMAGENET_CHARACTERISTIC_UUID,
                                           self.ImagenetCallback, indication=True)
        self.myme_device.handler.subscribe(JPEG_CHARACTERISTIC_UUID,
                                    self.FullImageCallback)
        self.myme_device.handler.subscribe(OCR_CHARACTERISTIC_UUID,
                                    self.OcrCallback, indication=True)
        self.myme_device.handler.subscribe(BARCODE_CHARACTERISTIC_UUID,
                                    self.BarcodeCallback, indication=True)

        self.myme_device.handler.subscribe(BATTERY_LEVEL_CHARACTERISTIC_UUID,
                                           self.battery_level_cb)
        self.myme_device.handler.subscribe(CHARGER_CHARACTERISTIC_UUID,
                                           self.charger_cb, indication=True)
        self.myme_device.handler.subscribe(TAP_CHARACTERISTIC_UUID,
                                           self.tap_cb, indication=True)
        self.myme_device.handler.subscribe(LOW_BATTERY_CHARACTERISTIC_UUID,
                                           self.low_battery_cb)


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

        with self.lock:
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

        if req.callback:
            self.sdk_scan_complete_cb(sorted_list, scan_state, error, req.callback)

        # done, signal the caller in case it is blocked
        req.event.set()

    def _handle_connection_request(self, req):
        if not self.myme_device.device_state == DeviceState.Paired:
            error=('Cannot connect to device because device is in an incorrect '
                   'state: {}. (Must be in Paired to connect'
                   ''.format(self.myme_device.device_state))
            self.sdk_connected_to_device_cb(None, error, req.callback)
            return

        self.set_device_state(DeviceState.Connecting)
        while not req.success:
            try:
                self.myme_device.handler = self.ble_adapter.connect(address=req.device_addr,
                        addr_type=constants.ble_address_type['gap_address_type_random'],
                        timeout=req.request_timeout)
                self._subscribe_to_all_services()
                self.set_device_state(DeviceState.Connected)
                self.sdk_connected_to_device_cb(req.device_addr, None, req.callback)

                self.get_characterstics_list()
                self.myme_device.fill_device_info()

                req.success = True
            except Exception as ex:
                self.set_device_state(DeviceState.Paired)
                req.success = False
                error= ('Failure when trying to connect to device at address: '
                        '{}\nException Message: {}\nRETRYING'
                        ''.format(req.device_addr, ex))
                traceback.print_exc()
                self.sdk_connected_to_device_cb(None, error, req.callback)


                time.sleep(1)
                self.ble_adapter.disconnect_all()
                self.ble_adapter.reset()

        req.event.set()

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
        except NotConnectedError:
            print_and_log('ERROR: tried writing to face_image characteristic '
                               'while not connected.', ERROR)


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
        face_id, timestamp, signature_int_array, flag = \
                       PacketParser.parse_face_signature_packet(res.packet)
        self.sdk_face_signature_cb(face_id, timestamp, signature_int_array, flag)

    def _handle_face_image_assembler_response(self, res):
        myme_face_id, detected_time, raw_image_bytearray = \
            PacketParser.parse_face_image_packet(res.packet)
        if myme_face_id is None:
            print_and_log('Error fetching face image!')
            return

        curr_req_list = \
            self.pending_requests[RequestType.FaceImageRequest].get(myme_face_id)
        for req in curr_req_list:
            # Use this opportunity to store face image into the DB
            self.sdk_face_image_cb(req.db_face_id, detected_time,
                                   raw_image_bytearray, req.callback)


    def _handle_full_image_assembler_response(self, res):
        myme_image = PacketParser.parse_full_image_packet(res.packet)
        curr_req_list = \
            self.pending_requests[RequestType.FullImageRequest].get(myme_image.frame_idx)
        for req in curr_req_list:
            self.sdk_full_image_cb(myme_image, res.callback)

    def _handle_imagenet_assembler_response(self, res):
        visual_topics_list, timestamp = \
            PacketParser.parse_imagenet_packet(res.packet)
        self.sdk_visual_topics_cb(visual_topics_list, timestamp)

    def _handle_ocr_assembler_response(self, res):
        ocr_lines_list, timestamp, is_frame_end = \
            PacketParser.parse_ocr_packet(res.packet)
        for line in ocr_lines_list:
            self.sdk_ocr_line_cb(line, timestamp)
        # if is_frame_end is true, call the callback with ocr_line = None
        if is_frame_end:
            self.sdk_ocr_line_cb(None, timestamp, is_frame_end)

    def _handle_item(self, req):
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

    def low_battery_cb(self, handle, packet):
        new_battery_state = PacketParser.parse_battery_state_packet(packet)
        if new_battery_state is not None:
            self.sdk_battery_state_updated_cb(new_battery_state)

    def battery_level_cb(self, handle, packet):
        battery_level = PacketParser.parse_battery_charge_level_packet(packet)
        if battery_level is not None:
            self.sdk_battery_charge_level_updated_cb(battery_level)

    def barcode_assembler_cb(self, packet):
        (barcode, timestamp) = PacketParser.parse_barcode_packet(packet)
        self.sdk_barcode_cb(barcode, timestamp)


