import serial
import struct

class Controller:
	BAUDRATE = 115200
	LINE_TERMINATOR = '\n'

	def __init__(self, serial_device, timeout = 1):
		self.serial = serial.Serial(serial_device, self.BAUDRATE, timeout = timeout)

	def disconnect(self):
		self.serial.close()

	def q_to_value(self, qValue, length):
		return qValue * (2 ** length)

	def value_to_q(self, value, length):
		return value / (2 ** length)

	def write(self, message):
		return self.serial.write(message + self.LINE_TERMINATOR)

	def readline(self):
		return self.serial.readline()

	def hello(self):
		return self.write('HEL')

	def arm(self):
		return self.write('ARM')

	def disarm(self):
		return self.write('DRM')

	def identify_motor(self):
		return self.write('IDM')

	def enable_throttle(self):
		return self.write('ECP1')

	def disable_throttle(self):
		return self.write('ECP0')

	def set_speed(self, speed_krpm):
		return self.write('SPD{}'.format(struct.pack('!l', self.q_to_value(speed_krpm, 24))))

	def set_speed_kp(self, speed_kp):
		return self.write('SKP{}'.format(struct.pack('!l', self.q_to_value(speed_kp, 24))))

	def set_speed_ki(self, speed_ki):
		return self.write('SKI{}'.format(struct.pack('!l', self.q_to_value(speed_ki, 24))))
