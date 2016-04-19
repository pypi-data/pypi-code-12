import socket, Queue
import base64
import numpy as np
import cv2
import rtp
import work
import logg
import threading

"""
	------	Python Plugin ( ImageSocket)	------
	This plugin is written by SunnerLi in 2016 - 04
	This class define the operator of ImageSocket
	The project is follow MIT License
"""

class ImageSocket():
	"""
		This class define the ImageSocket contain and method
	"""
	# Constant definition
	Def = -1
	TCP = 0
	UDP = 1
	mode = Def

	sock = None							# Socket object
	opSock = None						# Work socket object (TCP used)
	hadSetTimeout = False				# The flag to record if set the timeout of the socket
	semaphore = threading.Semaphore()	# The semaphore object
	messImage = []						# The list would record each string of image

	def __init__(self):
		"""
			Constructor of ImageSocket
		"""
		pass

	def socket(self, family, socketType):
		"""
			Construct the UDP socket
		"""
		self.sock = socket.socket(family,socketType)
		if socketType == socket.SOCK_DGRAM:
			self.mode = self.UDP
		elif socketType == socket.SOCK_STREAM:
			self.mode = self.TCP
			self.opSock = work.ImageSocket_Work()
		else:
			logg.LOG("This plugin didn't support other type of socket.")

	def setsockopt(self, n1, canReuse, n2):
		"""
			Set socket option
			It can set if the port number can be reuseable
		"""
		self.sock.setsockopt(n1, canReuse, n2)

	def bind(self, tuplee):
		"""
			Bind the port number and host address
			The input is the tuple
		"""
		self.sock.bind (tuplee)

	def listen(self, times):
		"""
			( TCP Only )
			Set the number of max listen request for one time
		"""
		if self.mode == self.TCP:
			self.sock.listen(times)
		elif self.mode == self.UDP:
			logg.LOG("UDP mode cannot call this function. Try to remove this call.")
		else:
			logg.LOG("Invalid mode cannot call this function.")

	def settimeout(self, _time=10):
		"""
			Set the timeout of the udp socket
		"""
		self.sock.settimeout(_time)

	def accept(self):
		"""
			( TCP Only )
			Accept the tcp connect request
			This function force to set timeout
		"""
		if self.mode == self.TCP:
			if not self.hadSetTimeout:
				self.settimeout(10)
			opSock, address = self.sock.accept()
			self.opSock.setWorkSocket(opSock)
			return self.opSock, address
		elif self.mode == self.UDP:
			logg.LOG("UDP mode cannot call this function. Try to remove this call.")
		else:
			logg.LOG("Invalid mode cannot call this function.")

	def recvfrom(self, size):
		"""
			( UDP Only )
			Recv the image string from the opposite
			This function force to set the timeout

			Notice: if there is any rtp package loss, it would return None
		"""
		if self.mode == self.UDP:
			self.semaphore.acquire()
			self.messImage = []
			if not self.hadSetTimeout:
				self.sock.settimeout(10)

			png = ""
			while True:
				try:
					data, addr = self.sock.recvfrom(size)
					logg.LOGI("length: ", len(data))
					r = rtp.RTP()
					#png += data[65:]
					r.decode(data[:65])
					breakFlag = r.getMarker()
					index = r.getIndex()

					if len(self.messImage) <= index:
						while len(self.messImage) <= index:
							self.messImage.append("")
					self.messImage[index] = data[65:]
					if breakFlag == 0:
						break
				except socket.timeout:
					data = ""
					break

			# Transform image string to numpy (Through OpenCV)
			png = self.formBase64String(self.messImage)
			if not png == None:
				png = base64.b64decode(png)
				png = self.formImgArr(png)
				png = self.oneD2Numpy(png)
			self.semaphore.release()
			return png
		elif self.mode == self.TCP:
			logg.LOG("TCP mode cannot call this function! Try ' recv() '")
		else:
			logg.LOG("Invalid mode cannot call this function.")

	def printWithASCII(self, data):
		"""
			Print the string by each character with ascii code.
			This function just used to debug
		"""
		for i in range(len(data)):
			print "arr[", i, "]: ", data[i], "\tASCII: ", ord(data[i])

	def formBase64String(self, data):
		"""
			Collect the list as base64 image string
		"""
		png = ""
		for i in range(len(data)):
			if data[i] != "":
				png += data[i]
			else:
				logg.LOGI("RTP package loss, position:", i)
				return None
		return png

	def formImgArr(self, data):
		"""
			Change the image string into 1D array
		"""
		png = []
		for i in range(len(data)):
			png.append(ord(data[i]))
		return png

	def oneD2Numpy(self, data):
		"""
			Decode the 1D image by the OpenCV
		"""
		data = np.asarray(data, dtype=np.uint8)
		data = cv2.imdecode(data, 1)
		return data

	def close(self):
		"""
			Close the socket
		"""
		self.sock.close()
		if self.mode == self.TCP:
			self.opSock.close()
