#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ptg_addbiggreactions: add a list bigg reactions to an existing sbml file,
making sure that the metabolites referenced by reactions are also present!"""

from __future__ import print_function

import argparse
import libsbml

from . import BiGG, SBMLutils, BiGG2SBML


__author__ = "Nicolas Loira"
__email__ = "nloira@gmail.com"
__date__ = "08/March/2016"


def drop_R(s):
	"""If exists, remove R_ prefix from reaction ids"""
	return s[2:] if s.startswith("R_") else s


def read_reaction_list(reaction_list_file):
	"""Parses a simple file with a list of reaction ids"""
	with open(reaction_list_file, 'r') as rlfd:
		reaction_list = [drop_R(l[:-1]) for l in rlfd]
	return reaction_list


def main():
	"""Add BiGG reactions to an existing SBML model"""
	# args
	parser = argparse.ArgumentParser(description="add reactions from a table, using BiGG 2.0 API")
	parser.add_argument("-s", "--sbml", required=True, help="SBML model where reactions will be added")
	parser.add_argument("-l", "--list", required=True, help="list with reactions to add")
	parser.add_argument("-o", "--output", required=True, help="output SBML file")
	args = parser.parse_args()

	sbmlfile = args.sbml
	reaction_list_file = args.list
	sbmlout = args.output

	# parse input
	BiGG.init()
	new_reactions = read_reaction_list(reaction_list_file)
	sbml = SBMLutils.read_sbml(sbmlfile)
	model = sbml.getModel()

	reactionsInModel = set([drop_R(r.getId()) for r in model.getListOfReactions()])
	reactionsAdded = set()

	# Add new reactions
	for reaction in new_reactions:
		if reaction not in reactionsAdded and reaction not in reactionsInModel:

			# try the same reactionid
			biggreaction = BiGG.get_bigg_reaction(reaction)
			if biggreaction is not None:
				BiGG2SBML.add_reaction(model, biggreaction)
				print("Adding reaction: " + biggreaction['bigg_id'])
				reactionsAdded.add(reaction)
				continue

			# else, look for old/alternative reactionid
			biggreaction = BiGG.guess_reaction(reaction)
			if biggreaction is not None:
				biggid = biggreaction['bigg_id']
				if (biggid not in reactionsAdded) and (biggid not in reactionsInModel):
					print("WARNING! replacing old reaction %s with: %s" % (reaction, biggid))
					BiGG2SBML.add_reaction(model, biggreaction)
					reactionsAdded.add(biggid)
				continue

			print("WARNING! no reaction %s in BiGG database" % (reaction))

	# close
	libsbml.writeSBMLToFile(sbml, sbmlout)
	BiGG.close()

if __name__ == '__main__':
	main()
