import zmq


class Messaging:
    def __init__(self, sockets_to_connect_to: list):
        context = zmq.Context()
        self.sub_socket = context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, b'')

        for socket in sockets_to_connect_to:
            self.sub_socket.connect(socket)
