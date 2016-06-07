#!/usr/bin/env python

import argparse
import hashlib
import ntpath
import os
from chkopy import GetHashofDest
from chkopy import GetHashofSource
from chkopy import path_leaf
from chkopy import md5
from shutil import copy2
from shutil import copytree
#version: 0.1.4b
#author: Christopher McFetridge
#date: 20160505

#specify optional arguments (e.g. -v) and positional arguments.
parser = argparse.ArgumentParser(description="Performs md5 checksum on file/direcotry source and destination.")
parser.add_argument("-v", "--verbosity", help="Increase verbosity--print checksums in terminal", action='store_true')
parser.add_argument("-r", "--recursive", help="Copies directory tree from one location to another. Destination directory must not exist, e.g. /Desktop/directory-to-be-created.", action='store_true')
parser.add_argument("-n", "--nullcopy", help="Experimental: nullifies copy commands. Allows chkopy to be used to compare checksums.", action='store_true')
parser.add_argument("csource", type=str, help="Copy source")
parser.add_argument("cdest", type=str, help="Copy destination")
args = parser.parse_args()
   
#if verbosity flag is called set variable verbosity to 1 else 0	
if args.verbosity == True:
	verbosity = 1
else:
	verbosity = 0

#if recursive flag is called use the recursive checksum function and copytree to copy directories
if args.recursive == True:
	checkone = GetHashofSource(args.csource, verbosity)
	
	#if null copy flag is False then copy directory
	if args.nullcopy <> True:
		copytree(args.csource, args.cdest)
		
	checktwo = GetHashofDest(args.cdest, verbosity)
else:
#if recursive flag is not called
	checkone = md5(args.csource)#set variable checkone equal to the md5 of csource
	#if nullcopy flag is False then copy the file
	if args.nullcopy <> True:
		copy2(args.csource,args.cdest)#actual copying function~~so simple!
	try:
		checktwo = md5(args.cdest)
	except IOError:
		trialfile = path_leaf(args.csource)
		trialpath = os.path.join(args.cdest, trialfile)
		checktwo = md5(trialpath)

#if verbosity flag is called print both checksums at end of operation		
if verbosity == 1:
	print "checksum of %r is --> %r" % (args.csource, checkone)
	print "checksum of %r is --> %r" % (args.cdest, checktwo)

#if
if args.recursive == True: 
	if source_array.keys() == dest_array.keys():
		print "Individual hashes match."
		if checkone <> checktwo:
			print "Directory level hashes do not match. Proceed with caution."
	else:
		print "Errors occurred copying the following files"
		for hashpacket, filename in source_array.items():
			if hashpacket not in dest_array:
				print "%r , %r" % (filename, hashpacket)	
else:	
	if checkone <> checktwo:	
		print "Individual hashes do not match."