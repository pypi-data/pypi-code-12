#!/usr/bin/env python
# encoding: utf-8

# This file is part of BioPantograph https://bitbucket.org/nloira/pantograph
# Copyright © 2009-2016 Nicolas Loira
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioPantograph.  If not, see <http://www.gnu.org/licenses/>.


"""
projector.py

Project an SBML model, based on a scaffold model and set of .rel files
Created by Nicolas Loira on 2010-12-28.
"""

import sys
import getopt
from .pathtastictools import SBMLmodel, MultiRelations


HELP_MESSAGE = '''
Project an SBML file from a scaffold model and a set or .rel files
usage: projector.py [-f curated.rel] scaffold.xml method1.rel [method2.rel...]
or print the current version id with: projector -v
'''

VERSION = "0.1.2"


def log(message):
	"""Print to stderr"""
	print >>sys.stderr, message

class Usage(Exception):
	"""Exception in case of demand of help or error parsing parameters"""
	def __init__(self, msg):
		super(Usage, self).__init__()
		self.msg = msg

def getForcedReactions(forceGAfile):
	"""check if we are forcing reactions and parse that file"""
	forcedReactions = None
	if forceGAfile:
		forcedReactions = dict()
		for line in open(forceGAfile):
			if line.startswith('#'):
				continue
			rid, newga = line[:-1].split("\t")
			forcedReactions[rid] = newga
			log("forcing: %s to (%s)" % (rid, newga))
	return forcedReactions


def parseParameters(argv):
	"""Parse parameters from command line"""
	forceGAfile = None
	output = None
	logFile = None

	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:vf:l:", ["help", "output=", "force=", "log="])
		except getopt.error, msg:
			raise Usage(msg)

		# option processing
		for option, value in opts:
			if option == "-v":
				print VERSION
				sys.exit()
			if option in ("-h", "--help"):
				raise Usage(HELP_MESSAGE)
			if option in ("-o", "--output"):
				output = value
			if option in ("-f", "--force"):
				forceGAfile = value
			if option in ("-l", "--log"):
				logFile = value


	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		sys.exit()

	return args, forceGAfile, output, logFile

def main(argv=None):
	"""Projector component of Pantograph. Takes a model and orthology files to produce a new model"""

	args, forceGAfile, output, logFile = parseParameters(argv)

	# check parameters
	# parse filenames from args
	if len(args) < 2:
		log(HELP_MESSAGE)
		return 2

	sbmlfile = args[0]
	relFiles = args[1:]

	# check if we are forcing reactions
	forcedReactions = getForcedReactions(forceGAfile)

	# logfile or stderr
	logFD = sys.stderr if logFile is None else open(logFile, 'w')

	# parse SBML
	model = SBMLmodel(sbmlfile, logFD)

	# a Relations class for each .rel file
	rels = MultiRelations(logFD=logFD)
	rels.loadMulti(relFiles)

	# DEBUG
	# print "DEBBUG: Checking rels"
	# rels.debugRels()

	# start unraveling among rels only

	rels.unravel1to1()
	rels.unravelDuplicates()

	# report findings
#	for k,v in rels.map1to1.iteritems():
#		print ">>>%s --> %s" % (str(k),str(v))
#	for k,v in rels.map1toN.iteritems():
#		print "@@@%s --> %s" % (str(k),str(v))

	# force new GAs to certain reactions
	if forceGAfile:
		model.forceGeneAssociations(forcedReactions)

	# rewrite GeneAssociations, using rels.unraveling and GAs.unraveling
	model.rewriteGeneAssociations2(rels)



	# clean resulting model
	model.removeReactions()

	# output projected model
	outfd = sys.stdout if output is None else open(output, "w")
	model.write(outfd)



if __name__ == "__main__":
	sys.exit(main())
