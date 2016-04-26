import socket


class ClientSocket(object):

    def __init__(self, message_length=1024):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_length = message_length
        self.connected = False

    def connect(self, host, port):
        self.socket.connect((host, port))
        self.connected = True

    def send(self, message):
        if not self.connected:
            raise UserWarning("Not connected to any remote host.")
        byte_message = str.encode(message)
        self.socket.send(byte_message)

    def receive(self):
        data = self.socket.recv(self.message_length)
        return data.decode("utf-8")

    def close(self):
        self.socket.close()
        self.connected = False
