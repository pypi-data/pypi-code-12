#!/usr/bin/env python

__version__ = '0.1'

import gpio
import time
import string

IN, OUT = 'in', 'out'
LOW, HIGH = 'low', 'high'

def getIOrank(pinstr):	
	pin  = 0
	base  = 0	
	#check if a int
	if isinstance(pinstr, int):	
		pin = pinstr
		
	#check if a string
	if isinstance(pinstr, str):
		pinstr=pinstr.upper()
		pinstr=pinstr.replace('GPIO','')	#delete GPIO
			
		#check the GPIO port
		if not pinstr.isdigit():	
			pos='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
			if pinstr[0] in pos :
				base = pos.find(pinstr[0])
				pinstr=pinstr[1:]
			else :
				print 'ERROR: wrong GPIO writing '	
				return	0		
		#the rest str should digit
		if pinstr.isdigit() :
			pin = string.atoi(pinstr)
		else :
			print 'ERROR: wrong GPIO writing '
			return 0

	return pin+base*32

class cgpio(object):
	def __init__(self, pinstr, mode, initial=False):	
		self.pin = getIOrank(pinstr)
		self.mode = mode
		gpio.setup(self.pin, self.mode, None, initial)

	def mode(self):
		return self.mode

	def set(self, value):
		return gpio.set(self.pin,value)

	def read(self):
		return gpio.read(self.pin)




'''this is a test'''
'''
t = cgpio('GPIOA9',OUT,HIGH)

t.set(1)
time.sleep(1)
t.set(0)
time.sleep(1)
t.set(1)
time.sleep(1)
t.set(0)

print
print
print 'Set INPUT mode'
t=cgpio('A9',IN)
print "pin:",t.pin, "mode:", t.mode
print t.read()
time.sleep(1)
print t.read()
time.sleep(1)
print t.read()
time.sleep(1)
print t.read()
time.sleep(1)
print t.read()
'''