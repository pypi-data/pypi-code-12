#!/usr/bin/env python
from __future__ import print_function
import logging, time, sys
logging.getLogger().setLevel(logging.DEBUG)
from rusocsci import buttonbox, utils
import time, serial

port = utils.serialList()[0]
#device, s = utils.open(port)
device = serial.Serial(port, baudrate=115200, parity='N', timeout = 0.0)

# reset
device.flushInput()
device.setDTR(False)
time.sleep(0.1)
device.setDTR(True)

t0 = time.time()
bytesRead = ""
while len(bytesRead) < 3 or bytesRead[-2:] != "\x0d\x0a":
	if time.time() > t0 + 3:
		logging.info("USB serial timeout waiting for ID string")
		print([device, "USB serial timeout"])
		exit()
	bytes = device.read()
	#if len(bytes) > 0:
		#print("bytes: #{}#".format(bytes))
	#if len(bytesRead) > 2:
		#print("bytesRead: #{}#".format(bytesRead[-3:]))
	bytesRead += bytes

print(bytesRead)