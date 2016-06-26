import pickle
from time import sleep

import zmq

from adapters.communication_messaging import ZmqMessaging


def main():
    context = zmq.Context()
    address = 'tcp://127.0.0.1:5678'
    pub = context.socket(zmq.PUB)
    pub.bind(address)
    sub = context.socket(zmq.SUB)
    sub.setsockopt(zmq.SUBSCRIBE, b'g')
    sub.connect(address)

    msg = (b'command_line', pickle.dumps(['MSG', 'Ben', 'This is the message']))
    # sort of expect an error here
    sleep(.5)
    pub.send_multipart(msg)


    while True:
        frame = sub.recv_multipart()
        print(pickle.loads(frame[1]))

    """
    messaging = ZmqMessaging('command_line',
                             'tcp://127.0.0.1:4000',
                             'tcp://127.0.0.1:4001')

    messaging.set_socket_filter('command_line')
    messaging.start_messaging()

    # reason I'm going to call this scratch is so the message I send 
    # has the right fromat
    second = ZmqMessaging('command_line',
                          'tcp://127.0.0.1:4000',
                          'tcp://127.0.0.1:4001')

    second.set_socket_filter('')
    second.start_messaging()

    # this is the message we're sending
    # ('scratch', 'test')
    sleep(.5)
    second.send_message('MSG', 'ben', 'test')

    while True:
        # if everything works should recv
        # ('scratch', 'test')
        frame = messaging.sub_socket.recv_pyobj()
        print(frame)
    """

if __name__ == '__main__':
    main()
