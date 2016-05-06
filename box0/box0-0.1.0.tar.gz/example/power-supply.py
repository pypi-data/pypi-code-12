#/bin/python

#
# box-v5 Power Supply
# Author: Kuldeep Singh Dhaka <kuldeepdhaka9@gmail.com>
# Licence: GPLv3 or later
#

import usb.core
import usb.util
from usb.util import CTRL_IN, CTRL_OUT, CTRL_RECIPIENT_DEVICE, CTRL_TYPE_VENDOR

BOX0V5_PS_EN_GET = 0x01
BOX0V5_PS_EN_SET = 0x02

POWER_ANALOG = 0x01
POWER_DIGITAL = 0x02

# python2 raw_input and python3 input
try: input = raw_input
except: pass

# open device
dev = usb.core.find(idVendor=0x1d50, idProduct=0x8085)
if dev is None:
	raise ValueError("Device not found")

# assign 1st configuration
dev.set_configuration()

print("Welcome! please enter a command:")
print("  b - [both] digital supply enable and analog supply enable")
print("  a - [analog] analog supply enable and digital supply disable")
print("  d - [digital] digital supply enable and analog supply disable")
print("  n - [none] digital supply disable and analog supply disable")
print("  s - [status] both suppy status")
print("  e - [exit] exit the program")

def power_supply_set(dev, analog, digital):
	"""
	Activate/deactive power supply
	dev: USB Device
	analog: activate/deactivate Analog supply
	digital: activate/deactivate Digital supply
	"""
	bmReqType = CTRL_OUT | CTRL_RECIPIENT_DEVICE | CTRL_TYPE_VENDOR
	mask = POWER_ANALOG | POWER_DIGITAL
	value = 0x00
	if analog: value |= POWER_ANALOG
	if digital: value |= POWER_DIGITAL
	wValue = (mask << 8) | value
	dev.ctrl_transfer(bmReqType, 0xFF, wValue, BOX0V5_PS_EN_SET)

def power_supply_get(dev):
	"""
	Read power supply status
	dev: USB Device
	return a tuple (<analog-supply>, <digital-supply>)
	"""
	bmReqType = CTRL_IN | CTRL_RECIPIENT_DEVICE | CTRL_TYPE_VENDOR
	data = dev.ctrl_transfer(bmReqType, 0xFF, 0, BOX0V5_PS_EN_GET, 1)
	analog = (data[0] & POWER_ANALOG) != 0x00
	digital = (data[0] & POWER_DIGITAL) != 0x00
	return analog, digital

#turn both supply off
power_supply_set(dev, False, False)

try:
	while True:
		c = input("> ")
		if c == "b":
			power_supply_set(dev, True, True)
		elif c == "a":
			power_supply_set(dev, True, False)
		elif c == "d":
			power_supply_set(dev, False, True)
		elif c == "n":
			power_supply_set(dev, False, False)
		elif c == "s":
			analog, digital = power_supply_get(dev)
			print("Analog: " + ("Enabled" if analog else "Disabled"))
			print("Digital: " + ("Enabled" if digital else "Disabled"))
		elif c == "e":
			break;
		else:
			print("unknown command: " + c)
except KeyboardInterrupt: pass

#turn all supply off
power_supply_set(dev, False, False)

#close device
del dev
