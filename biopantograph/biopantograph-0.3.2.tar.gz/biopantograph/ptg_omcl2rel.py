#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
omcl2rel.py

Parses OrthoMCL output and translate it to a simple .rel file
Created by Nicolas Loira on 2010-06-15.
"""


import sys
from collections import defaultdict
import getopt

VERSION="0.1.2"




#### params
def main():


	def printrel(genes):
		if len(genes[source])>0 or len(genes[target])>0:
			outfd.write(",".join( [rename.get(g,g) for g in genes[target]]) + \
				"\t" + \
				",".join( [rename.get(g,g) for g in genes[source]]) + "\n")


	output = None
	corrFile = None
	rename=dict()

	format=None

	source = 'scer'
	target = 'ylip'

	targetTranslator={
	'CAGL':'cgla',
	'DEHA':'dhan',
	'KLLA':'klac',
	'YALI':'ylip'
	}

	opts, args = getopt.getopt(sys.argv[1:], "ho:vs:t:2", ["help", "output=", "corr=", "source=", "target=","format="])

	for o, v in opts:
		if o == "--corr": corrFile=v
		if o in ("-s","--source"): source=v
		if o in ("-t","--target"): target=v
		if o in ("--format"): format=v
		if o == "-2": format="format2"
		if o == "-v":
			print VERSION
			return 0
		if o in ("-o","--output"):
			output = v



	groupfile = args[0]

	# output to file?
	if output is not None:
		outfd = open(output,"w")
	else:
		outfd = sys.stdout


	# try to guess format
	if format==None:
		groupsFD=open(groupfile)
		l=groupsFD.readline()
		if l.find("\t")>-1:
			format="format2"
		else:
			format="format1"
		groupsFD.close()



	# rename target to omcl standard
	if target in targetTranslator:
		target=targetTranslator[target]

	### Correlation

	if corrFile:
		for line in open(corrFile):
			elems=line[:-1].split()
			rename[elems[0]]=elems[1]


	#### parse groups

	if format=="format1":
		for line in open(groupfile):
			elems = line[:-1].split()
			genes=defaultdict(list)
			for e in elems[1:]:
				parts = e.split("|")
				genes[parts[0]].append(parts[1])
			printrel(genes)
	elif format=="format2":
		for line in open(groupfile):
			elems = line[:-1].split('\t')
			elems = elems[1].split()
			genes=defaultdict(list)
			for e in elems:
				parts = e[:-1].split("(")
				# print parts[0],parts[1]
				genes[parts[1]].append(parts[0])
			printrel(genes)
	else:
		assert "No default format?"

	# closing
	outfd.close()


	#	if len(genes['ylip'])>0 or len(genes['scer'])>0:
	#		print ",".join(genes['ylip'])+"\t"+",".join(genes['scer'])
		# for omcl
		
		# use the name in omcl in case we cannot translate it (but remove the 'xxxx|' orgID at the begginig)


if __name__ == '__main__':
    main()

