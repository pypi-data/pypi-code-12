#!/usr/bin/env python


import gpio
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


	def pinWrite(self, value):
		return gpio.set(self.pin,value)

	def pinRead(self):
		return gpio.read(self.pin)

	def setmode(mode,initial=False):
		return gpio.setup(self.pin, mode, None, initial)

	def getmode(self):
		return self.mode
