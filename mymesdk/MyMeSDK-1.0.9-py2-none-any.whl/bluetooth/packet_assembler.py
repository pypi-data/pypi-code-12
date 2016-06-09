
import struct
from ..utils.sdk_utils import print_and_log, ERROR, EXCEPTION

PACKET_MIN_SIZE = 1 + 4

class PacketAssembler(object):
    """
    This class assembels packets sent from the MyMe device into one message
    """
    def __init__(self, callback):
        """
         :param callback - the callback to be called upon packet completion
         :return:
         """
        self.callback = callback
        self.current_data = bytearray()
        self.total_expeceted_len = 0

    def reset(self):
        """
        resets the state of the PacketAssembler, removing any current stored data
         and allowing new data to be sent.

        :return:
        """
        self.total_expeceted_len = 0
        self.current_data = bytearray()

    def send(self, packet):
        """
        sends a anew packet to be assmebled.
        Call this method for each new packet.
        Once fully assembled the calllback given on init would be called
        After that, new calls to send might be done (without need to call the 'reset' API).
        :return:
        """
        if self.total_expeceted_len == 0:
            if len(packet) < PACKET_MIN_SIZE:
                print_and_log('got packet of wrong size {0}'.format(len(packet)), ERROR)
                self.reset()
                return

            # first packet, parse the header to get the size
            # < - little endian, x-padding, I - unsigned byte
            self.total_expeceted_len = struct.unpack('<xI', str(packet[0:5]))[0]

        self.current_data += (packet)

        # check if we've reached the end
        if len(self.current_data) >= self.total_expeceted_len:
            # the data is not expected to be bigger than the expected total
            if len(self.current_data) > self.total_expeceted_len:
                print_and_log('total size of data {0} is bigger than expected '
                    '{1}! Throwing away.'.format(
                    len(self.current_data), self.total_expeceted_len), ERROR)
                self.reset()
                return

            else:
                self.callback(self.current_data)
                self.reset() # cleanup
