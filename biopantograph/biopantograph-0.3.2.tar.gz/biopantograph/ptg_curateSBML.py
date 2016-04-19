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
curateSBML.py: add new species and reactions from CSV files
"""

import sys
import getopt
from xml.etree.ElementTree import *
import csv

help_message = '''
Patches an SBML with new reactions and species from a csv file.
Usage: curateSBML --sbml draftModel.xml -s speciesPatch.csv -r reactionPatch.csv > curatedModel.xml
'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

class Species():
	def __init__(self, **kw):
		self.__dict__.update(kw)

class Reaction():
	def __init__(self, **kw):
		self.__dict__.update(kw)

	
def exiterror(errmsg=help_message):
	print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(errmsg)
	print >> sys.stderr, "\t for help use --help"
	sys.exit(2)

def log(msg):
	print >>sys.stderr, msg

def readcsv(filename):
	reader = csv.reader(open(filename))
	return reader

def parseSpecies(speciesFile):
	assert speciesFile
	
	allSpecies=[]
	for line in readcsv(speciesFile):
		if line[0] in ("", "ID"): continue
		allSpecies.append(Species( id=line[0], name=line[1], formula=line[2], compartment=line[3], boundary=False))

	return allSpecies


def parseReactions(reactionsFile):
	assert reactionsFile

	allReactions=[]
	for line in readcsv(reactionsFile):
		if line[0] in ("", "ID"): continue
		if line[0].startswith('#'): continue
		allReactions.append(Reaction( id=line[0], name=line[1], reversibility=line[2], reactants=line[3].split(';'), products=line[4].split(';'), geneassociation=line[5], genenameassociation=line[6], formula=line[7]))

	return allReactions

def getStoichiometry(species):
    if species.find("*")>-1:
        return species.split("*",1)
    else:
        return ("1.0", species)

class Model(object):
	def __init__(self, xmlFile):
		assert xmlFile
		model = parse(open(xmlFile))
		root=model.getroot()
		URI,tag= root.tag[1:].split("}",1)
		self.root=root
		self.URI=URI
		self.tag=tag
		self.HTMLTAG="http://www.w3.org/1999/xhtml"
		
		
		assert self.URI, "URI was not set correctly."
		
		# get a list of all known species and reactions (IDs)
		speciesNodes = root.findall("*/{%s}listOfSpecies/{%s}species" % (URI,URI))
		self.speciesIDs = [s.get('id') for s in speciesNodes]
		
		reactionNodes = root.findall("*/{%s}listOfReactions/{%s}reaction" % (URI,URI))
		self.reactionIDs = [r.get('id') for r in reactionNodes]
		
		# remember listOf... objects
		self.listOfSpecies = root.findall("*/{%s}listOfSpecies" % (URI))[0]
		self.listOfReactions = root.findall("*/{%s}listOfReactions" % (URI))[0]
		
		# map of all parents (useful for removing nodes)
		self.parentMap = dict((c, p) for p in root.getiterator() for c in p)
		
	def u(self, tag):
		return "{%s}%s" % (self.URI, tag)


	def addSpecies(self, newSpecies):
		for s in newSpecies:
			if s.id not in self.speciesIDs:
				# we'll create a new species and add it to the list of species
				newSpecies = SubElement(self.listOfSpecies, "{%s}species" % (self.URI) , id=s.id, name=s.name, compartment=s.compartment)
				if s.compartment=="boundary":
					newSpecies.attrib['boundaryCondition']="true"
			else:
				log("Warning: trying to patch existing species id: "+s.id)

	def addReactions(self, newReactions):
		for r in newReactions:
			if r.id not in self.reactionIDs:
				# we'll create a new species and add it to the list of species
				newReaction = SubElement(self.listOfReactions, "{%s}reaction" % (self.URI) , id=r.id, name=r.name, reversible=r.reversibility)
				# add notes only if needed
				if (r.geneassociation!=""):
					notes = SubElement(newReaction, "{%s}notes" % (self.URI))
					body = SubElement(notes, "{%s}body" % (self.HTMLTAG), xmlns=self.HTMLTAG)
					p1 = SubElement(body, "{%s}p" % (self.HTMLTAG) )
					p1.text="GENE_ASSOCIATION: "+r.geneassociation
				# add reactants and products
				if (len(r.reactants)>0 and r.reactants[0]!=""):
					listOfReactants = SubElement(newReaction, "{%s}listOfReactants" % (self.URI))
					for reactant in r.reactants:
						s,m=getStoichiometry(reactant)
						spref= SubElement(listOfReactants, "{%s}speciesReference" % (self.URI), species=m.strip(), stoichiometry=s )
					
				if (len(r.products)>0 and r.products[0]!=""):
					listOfProducts = SubElement(newReaction, "{%s}listOfProducts" % (self.URI))
					for product	 in r.products:
						s,m=getStoichiometry(product)
						spref= SubElement(listOfProducts, "{%s}speciesReference" % (self.URI), species=m.strip(), stoichiometry=s)
				
				# add kineticLaw
				self.addKineticLaw(newReaction, r.reversibility)
						
			# r.id already in existing reactions!
			else:
				log("Warning: trying to patch existing species id: "+s.id)

	def addKineticLaw(self, reaction, reversible="true"):
		"""
	    <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <ci> dummy_flux </ci>
          </math>
          <listOfParameters>
            <parameter id="LOWER_BOUND" value="0" units="flux_unit"/>
            <parameter id="UPPER_BOUND" value="INF" units="flux_unit"/>
            <parameter id="OBJECTIVE_COEFFICIENT" value="0" units="dimensionless"/>
          </listOfParameters>
        </kineticLaw>
		"""
		
		# add kineticLaw tags
		kineticElement=SubElement(reaction, "{%s}kineticLaw" % self.URI)
		mathElement = SubElement(kineticElement, "{%s}math" % "http://www.w3.org/1998/Math/MathML")
		ciElement = SubElement(mathElement, "{%s}ci" % "http://www.w3.org/1998/Math/MathML")
		ciElement.text= " dummy_flux "
		
		lopElement=SubElement(kineticElement, "{%s}listOfParameters" % self.URI)
		parLow=SubElement(lopElement, self.u("parameter"), id="LOWER_BOUND", units="flux_unit", value="-INF")
		parUpp=SubElement(lopElement, self.u("parameter"), id="UPPER_BOUND", units="flux_unit", value="INF")
		parObj=SubElement(lopElement, self.u("parameter"), id="OBJECTIVE_COEFFICIENT", units="dimensionless", value="0")

		if reversible in ("false", "0"):
			parLow.attrib['value']="0"
			
	def write(self):
		print '<?xml version="1.0" encoding="UTF-8"?>'
		print tostring(self.root)
	


def addSpeciesMula(xmlFile):
	assert xmlFile
	
	model = parse(open(xmlFile))
	root=model.getroot()
	URI,tag= root.tag[1:].split("}",1)
	assert URI, "URI was not set correctly."
	speciesNodes = root.findall("*/{%s}listOfSpecies/{%s}species" % (URI,URI))

	# get list of species
	speciesIds = [s.get('id') for s in speciesNodes]

	# this is the listOfSpecies object
	listOfSpecies = root.findall("*/{%s}listOfSpecies" % (URI))[0]

	toAdd=('mula1', 'mula2', 's_2973_b', 'mula4')

	for sm in toAdd:
		if sm not in speciesIds:
			# we'll create a new species and add it to the list of species
			newSpecies = SubElement(listOfSpecies, "{%s}species" % (URI) , id=sm, name="name_"+sm, compartment="c_mula")
		else:
			log("Warning: trying to patch existing species id: "+sm)
	
	# write output
	# print tostring(root)
	
	

def main(argv=None):

	sbmlfile=None
	speciesPatch=None
	reactionsPatch=None

	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:vs:r:", ["help", "output=", "sbml="])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-o", "--output"):
				output = value
			if option=="--sbml":
				sbmlfile = value
			if option in ("-s"):
				speciesPatch = value
			if option in ("-r"):
				reactionsPatch = value

	except Usage, err:
		exiterror(err.msg)

	# validate inputs
	if not (sbmlfile and speciesPatch and reactionsPatch):
		exiterror()

	# log("sbmlfile:"+sbmlfile)
	# log("speciesfile:"+speciesPatch)
	# log("reactionsfile:"+reactionsPatch)

	# all ok, so call test method 
	model=Model(sbmlfile)

	newSpecies=parseSpecies(speciesPatch)
	newReactions=parseReactions(reactionsPatch)

	model.addSpecies(newSpecies)
	model.addReactions(newReactions)

	model.write()
	# that's all, folks!
	


if __name__ == "__main__":
	sys.exit(main())
