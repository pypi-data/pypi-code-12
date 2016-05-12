#!/bin/python

def file_ext(filename):
	import os
	ext = os.path.splitext(filename)[1]
	print ext

def is_ext(filename, ext):
	import os
	file_ext = os.path.splitext(filename)[1]
	if ext == file_ext:
		print "Files match"
	else:
		print "Files don't match"

def hello():
	"Saqib is awesome"