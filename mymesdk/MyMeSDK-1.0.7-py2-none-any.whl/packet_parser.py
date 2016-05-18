from __future__ import division # to get correct integers division

import datetime
import struct



from myme_objects import MyMeFace, MyMeImage, BoundingBox, OcrLine
from utils.sdk_utils import print_and_log, ERROR, bytearray_to_image
from myme_visual_topic import *
from constants import *


HEADER_PACKET_MIN_SIE  = 1 + 4 + 4 + 4

class PacketParser(object):

    @staticmethod
    def _parse_packet_header(packet):
        """
        Packet is in the form of a bytearray
        example: bytearray(b'\xd5\xb0)' (a packet of 2 bytes)
        :param packet:
        :return:
        """
        """
        message format:
        1 byte -  header - future use
        4 bytes - total length, including header
        4 bytes - signature index (running number)
        4 bytes -  timestamp, seconds from epoch
        variable length  - signature/jpeg data
        """

        if len(packet) < HEADER_PACKET_MIN_SIE:
            return None

        # <B means little endian unsigned byte
        (header, size, id, timestamp) =  struct.unpack('<BIII', str(packet[0:13]))
        # rest of the payload, returned as is
        payload = packet[13:]

        # make sure size in header matches acutal size of packet received
        if size != len(packet):
            print_and_log('ERROR: got unexpected size of packet {0} instead of {1}. '
            'Ignoring.'.format(len(packet), size),ERROR)
            return None

        return header, size, id, timestamp, payload

    @staticmethod
    def parse_time_packet(packet):
        curr_time = struct.unpack('<I', str(packet))[0]
        return datetime.datetime.utcfromtimestamp(curr_time)

    @staticmethod
    def parse_face_image_packet(packet):
        header, size, myme_id, detected_time, raw_image_bytearray = \
            PacketParser._parse_packet_header(packet)
        if header is not None:
            return myme_id, detected_time, raw_image_bytearray
        else:
            return None, None, None

    @staticmethod
    def parse_full_image_packet(packet):
        header, size, frame_idx, timestamp, payload = \
            PacketParser._parse_packet_header(packet)
        if header is not None:
            full_image = bytearray_to_image(payload)
            return MyMeImage(frame_idx, datetime.datetime.utcfromtimestamp(timestamp),
                             full_image)
        return None


    @staticmethod
    def parse_charger_packet(packet):
        int_state = int(struct.unpack('<B', str(packet))[0])
        try:
            charger_state = ChargerState(int_state)
        except ValueError:
            print_and_log('ERROR: got unexpected charger state value {0}.'
            'Ignoring.'.format(int_state),ERROR)
            return None
        return charger_state

    @staticmethod
    def parse_light_level_packet(packet):
        int_level =  int(struct.unpack('<B', str(packet))[0])
        try:
            light_level = LightLevel(int_level)
        except ValueError:
            print_and_log('ERROR: got unexpected light level value {0}.'
            'Ignoring.'.format(int_level),ERROR)
            return None
        return light_level

    @staticmethod
    def parse_version_packet(packet):
        try:
            version_str = packet.decode("utf-8")
        except Exception as ex:
            'Error trying to parse version packet.\nException Msg: {}'.format(ex)
            version_str = ''

        return version_str

    @staticmethod
    def parse_battery_state_packet(packet):
        int_state = int(struct.unpack('<B', str(packet))[0])

        try:
            battery_state = BatteryState(int_state)
        except ValueError:
            print_and_log('ERROR: got unexpected battery state value {0}.'
            'Ignoring.'.format(int_state),ERROR)
            return None
        return battery_state

    @staticmethod
    def parse_battery_charge_level_packet(packet):
        """
        Battery charge level packet:
        1 byte - battery level from 0 to 100 percent (unsigned 8 bit)
        :param packet:
        :return:
        """
        try:
            int_level = int(struct.unpack('<B', str(packet))[0])

        except Exception as ex:
            print_and_log('ERROR when parsing batter charge level packet.'
                          'Packet length: {}.'.format(len(packet)))
            int_level = 0

        return int_level

    @staticmethod
    def parse_face_signature_packet(packet):

        # parse header
        header, size, myme_face_id, timestamp, payload = \
            PacketParser._parse_packet_header(packet)
        if header is None:
            return None

        sig_num_bytes = len(payload)
        # <b means little endian signed byte
        signature_int_array = list(struct.unpack('<{}b'.format(sig_num_bytes),
                                            str(payload)))

        if header is not None:
            return myme_face_id, timestamp, signature_int_array, header
        return None


    @staticmethod
    def parse_imagenet_packet(packet):
        header, size, frame_idx, timestamp, payload = PacketParser._parse_packet_header(packet)

        if header is None:
            return None

        visual_topcis_list = []
        i = 0
        while i < len(payload):
            # <B means little endian unsigned byte
            probability = struct.unpack('<B', str(payload[i:i+1]))[0]
            i += 1

            j = i # store word start index

            # find end of the (null terminated string).
            # also stop if reached the end of the payload
            # (should not happen in well formatted packet)
            while payload[i] != 0 and i < len(payload):
                i += 1

            # decode to string
            topic = payload[j:i].decode("utf-8")

            # create the current visual_topic
            visual_topcis_list.append(VisualTopic(topic, probability))

            # continue to next topic
            i += 1

        return visual_topcis_list, datetime.datetime.utcfromtimestamp(timestamp)

    # takes an integer input which is expceted to be between 0-65535
    # normilizes the value between 0-1 returning the (float) result
    @staticmethod
    def bounding_box_coordinate_to_float(x):

        MAX_UNSIGNEDD_SHORT = 65535
        if x < 0 or x > MAX_UNSIGNEDD_SHORT:
            print_and_log('ERROR: got unexpected OCR '
                          'bounding box coordinate {0}.'
                          .format(x),ERROR)
            return 0
        return x/65535

    @staticmethod
    def parse_barcode_packet(packet):
        # parse header
        flag, size, frame_idx, timestamp, payload = PacketParser._parse_packet_header(packet)

        if flag is None:
            return None

        i = 0

        # find end of type (null terminated string).
        # also stop if reached the end of the payload
        # (should not happen in well formatted packet)
        while payload[i] != 0 and i < len(payload):
            i += 1

        # decode to string, default of ascii is used
        barcode_type = payload[0:i].decode()

        # find end of value (null terminated string).
        i+=1
        j = i
        while payload[i] != 0 and i < len(payload):
            i += 1

        # decode to string, default of ascii is used
        barcode_value = payload[j:i].decode()

        return barcode_type, barcode_value, datetime.datetime.utcfromtimestamp(timestamp)

    @staticmethod
    def parse_ocr_packet(packet):
        # parse header
        # flag: 0: normal ocr line packet
        #       1: "OCR-Frame-end" packet (packet may be empty or contain OCR line(s))
        #
        flag, size, frame_idx, timestamp, payload = PacketParser._parse_packet_header(packet)

        if flag is None:
            return None

        # now data itself
        # 1 byte - future use
        # bounding box, given using shorts (2 bytes)
        # 2 bytes - x pos
        # 2 bytes - y pos
        # 2 bytes - width
        # 2 bytes - height
        # 4 bytes - length of text line below,
        #  			 not including the length field itself, including null termination
        #  <variable length> - null terminated utf8 encoded string
        i = 0
        ocr_lines_list = []
        while i < len(payload):
            i += 1 # skip the first 'future-use' byte

            # prase boundinb box
            (x, y ,w ,h) = struct.unpack('<HHHH', str(payload[i:i+8]))

            box = BoundingBox(PacketParser.bounding_box_coordinate_to_float(x),
                            PacketParser.bounding_box_coordinate_to_float(y),
                            PacketParser.bounding_box_coordinate_to_float(w),
                            PacketParser.bounding_box_coordinate_to_float(h))

            # string length
            i += 8
            str_len = struct.unpack('<I', str(payload[i:i+4]))[0]

            i+=4
            j = i # store string start index

            # find end of the (null terminated string).
            # also stop if reached the end of the payload
            # (should not happen in well formatted packet)
            while payload[i] != 0 and i < len(payload):
                i += 1

            # validate length of the string matches the one speicifed in the packet
            if str_len != i-j:
                print_and_log('got unexpected ocr line length '
                          '{0} instead of {1}.'
                          .format(str_len, i-j),ERROR)

            # decode to string
            try:
                text_line = payload[j:i].decode("utf-8")
                # append to list
                ocr_lines_list.append(OcrLine(text_line, box))
            except UnicodeDecodeError:
                print_and_log('error decoding string {0}.'
                        .format(payload[j:i]),ERROR)

            # continue to next line
            i += 1

        return ocr_lines_list, datetime.datetime.utcfromtimestamp(timestamp), flag



