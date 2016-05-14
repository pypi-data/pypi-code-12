import zmq
import time

context = zmq.Context()
subscriber = context.socket(zmq.SUB)

subscriber.connect('tcp://192.168.2.199:43125')

try:
    z = subscriber.recv_multipart(zmq.NOBLOCK)
except zmq.error.Again:
    print('ok')
    time.sleep(1)

print('done')
