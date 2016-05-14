import zmq
import random
import sys
import time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)

while True:
    # socket.send_string("Server message to client3")
    [address, contents] = socket.recv_multipart()
    print("[%s] %s" % (address, contents))


    # msg = socket.recv()
    #  print (msg)
    time.sleep(1)