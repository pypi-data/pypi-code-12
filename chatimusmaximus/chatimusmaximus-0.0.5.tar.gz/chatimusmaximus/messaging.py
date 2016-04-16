from PyQt5 import QtCore
import zmq
from threading import Thread


class ZmqMessaging(QtCore.QObject):
    message_signal = QtCore.pyqtSignal(str, str, str)
    connected_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        context = zmq.Context()
        self.sub_socket = context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.thread = Thread(target=self.recv_sub_socket, daemon=True)
        self.thread.start()

    def subscribe_to_publishers(self, addresses: list):
        for address in addresses:
            self.sub_socket.connect(address)

    def recv_sub_socket(self):
        while True:
            frame = self.sub_socket.recv_pyobj()
            frame_length = len(frame)
            if frame_length == 4:
                del frame[1]
                self.message_signal.emit(*frame)
            elif frame_length == 2:
                state = frame[1]
                if state == 'CONNECTED':
                    state = True
                else:
                    state = False
                self.connected_signal.emit(state, frame[0])
