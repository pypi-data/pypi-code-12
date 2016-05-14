import zmq
import random
import sys
import time

port = "5666"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
# socket.connect("tcp://localhost:%s" % port)
socket.connect("tcp://*:%s" % port)

#socket.bind("tcp://*:%s" % port)

while True:
    # msg = socket.recv_string()
    # print (msg)
    socket.send_multipart([b"B", b"We would like to see this"])
    # socket.send_string("client message to server1")
    # socket.send_string("client message to server2")
    time.sleep(1)
