"""
 Box0 I2C Utilility

 help                       print this help
 help CMD                   print help on specific command [TODO]
 detect                     detect slave
 ping ADDR                  print 'pong' if slave reply
 read ADDR NUM              read from slave
 write ADDR DATA            write to slave [TODO]
 write8read ADDR BYTE NUM   write to slave
 id ADDR                    print slave identity

 where:
  CMD  = command name
  ADDR = 7bit slave address
  NUM  = number greater than 0
  BYTE = 1 byte
  DATA = byte array
"""

from docopt import docopt
import box0
import sys
import numpy as np
np.set_printoptions(formatter={'int':hex})

# http://stackoverflow.com/a/7321970/1500988
try: input = raw_input
except NameError: pass


class I2CUtil:
	def __init__(self):
		"find device"
		try:
			self.device = box0.usb.open_supported()
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())
			return

		"find module"
		try:
			self.i2c = self.device.i2c(0)
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())
			self.device.close()
			return

		"constraint logging"
		try:
			self.device.log(box0.LogLevel.WARN)
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def __deinit__(self):
		try:
			self.i2c.close()
			self.device.close()
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def id(self, params):
		if len(params) < 1:
			print("paramter missing, see help")
			return

		try:
			sid = int(params[0], 0)
			manuf, part, rev = self.i2c.slaveId(sid)
			info =	"MANUF " + str(hex(manuf)) + \
					", PART " + str(hex(manuf)) + \
					", REV " + str(hex(rev))
			print(info)
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def ping(self, params):
		if len(params) < 1:
			print("paramter missing, see help")
			return

		try:
			sid = int(params[0], 0)
			if self.i2c.slaveDetect(sid):
				print("pong")
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def read(self, params):
		if len(params) < 2:
			print("paramter missing, see help")
			return

		try:
			sid = int(params[0], 0)
			count = int(params[1], 0)
			readed = self.i2c.read(sid, count)
			print(str(readed))
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def help(self, params):
		print(__doc__)

	def detect(self, params):
		for i in range(0, 128):
			try:
				if self.i2c.slaveDetect(i):
					print("found @ " + str(hex(i)))
			except box0.ResultException as e:
				print("ERROR: " + str(e) + " " + e.explain())
				break

	def write8Read(self, params):
		"addr byte num"
		if len(params) < 3:
			print("paramter missing, see help")
			return
		try:
			sid = int(params[0], 0)
			write = int(params[1], 0)
			count = int(params[2], 0)
			readed = self.i2c.write8Read(sid, write, count)
			print(str(readed))
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def write(self, params):
		if len(params) < 2:
			print("paramter missing, see help")
			return
		try:
			sid = int(params[0], 0)
			params = params[1:]
			data = []
			for p in params:
				data.append(int(p, 0))

			self.i2c.write(sid, np.asarray(data, dtype=np.uint8))
		except box0.ResultException as e:
			print("ERROR: " + str(e) + " " + e.explain())

	def poll(self, cmd):
		params = cmd.split(" ")
		tag = params[0]
		params = params[1:]

		if tag == "detect":
			self.detect(params)
		elif tag == "ping":
			self.ping(params)
		elif tag == "help":
			self.help(params)
		elif tag == "read":
			self.read(params)
		elif tag == "write8Read" or tag == "write8read":
			self.write8Read(params)
		elif tag == "id":
			self.id(params)
		elif tag == "write":
			self.write(params)
		else:
			print("Unknown command!")

if __name__ == '__main__':
	util = I2CUtil()
	util.help("")

	while True:
		cmd = input("Box0 I2C: ")
		if len(cmd):
			util.poll(cmd)

	del util
