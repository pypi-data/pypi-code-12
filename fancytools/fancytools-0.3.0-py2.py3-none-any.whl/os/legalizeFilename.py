#!/usr/bin/python
# -*- coding: utf-8 -*-
import string#, unicodedata


def legalizeFilename(filename):
	validFilenameChars = "/-_.%s%s" % (string.ascii_letters, string.digits)
	replaceDict = {
		" ":"-",
		"ä":"ae",
		"ö":"oe",
		"ü":"ue",
		'µ':'mue'}
	for key in replaceDict:
		filename = filename.replace(key, replaceDict[key])
	return ''.join(c for c in filename if c in validFilenameChars)[:255]



if __name__ == '__main__':
	fname = 'jhgü6"!§$%&/jhgdfpol ü+öwq.jpeg'
	print("a save filename for %s would be %s" %(fname, legalizeFilename(fname)) )