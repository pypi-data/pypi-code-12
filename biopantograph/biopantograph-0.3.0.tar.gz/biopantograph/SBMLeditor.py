#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import itertools
from pprint import pprint

import libsbml

from .SBMLutils import log

MAX_FLOW_BOUND = 999999

"""High level model edit operations/verbs over libsbml"""

__author__ = "Nicolas Loira"
__email__ = "nloira@gmail.com"
__date__ = "14/March/2016"

already_moved = dict()

def valid_compartment(model, compartment):
	compartments = [c.getId() for c in model.getListOfCompartments()]
	return compartment in compartments


def move_reaction(model, reactionid, source_comp, target_comp):
	"Move species associated to this reaction, from source compartment to target compartment. Create species if necessary"
	assert model is not None

	if not valid_compartment(model, source_comp) or not valid_compartment(model, target_comp):
		log("MOVE: invalid compartments (%s,%s)" % (source_comp, target_comp))
		return False

	reaction = model.getReaction(reactionid)
	speciesReferences = itertools.chain(reaction.getListOfProducts(), reaction.getListOfReactants())
	
	for sr in speciesReferences:
		sid = sr.getSpecies()
		species = model.getSpecies(sid)
		if species is None:
			sr.setSpecies(already_moved[sid])  # probably already moved
		elif species.getCompartment() == source_comp:
			log("Moving %s from [%s] to [%s]" % (species.getId(), source_comp, target_comp))
			new_speciesid = move_species(model, sid, source_comp, target_comp)
			sr.setSpecies(new_speciesid)

	return True


def move_species(model, speciesid, source_comp, target_comp):
	global already_moved

	if speciesid in already_moved:
		return already_moved[speciesid]

	species = model.getSpecies(speciesid)
	assert species.getCompartment() == source_comp

	# if there is an existing species at the target compartment, use that one
	# else, create a new one with the same characteristics

	new_speciesid = speciesid[:-1] + target_comp
	
	if model.getSpecies(new_speciesid) is None:
		new_species = species.clone()
		new_species.setCompartment(target_comp)
		new_species.setId(new_speciesid)
		log(" Cloning %s to %s" % (speciesid, new_species.getId()))
		model.addSpecies(new_species)
		model.removeSpecies(speciesid)
	else:
		log(" Using existing "+new_speciesid)

	already_moved[speciesid] = new_speciesid
	return new_speciesid


def remove_compartment(model, compartmentid):
	
	# remove all species associated to this compartment
	for species in list(model.getListOfSpecies()):
		if species.getCompartment() == compartmentid:
			model.removeSpecies(species.getId())

	# remove all related reactions
	reactionids = reactions_touching_compartment(model, compartmentid)
	for r in reactionids:
		model.removeReaction(r)

	# now remove the compartment
	model.removeCompartment(compartmentid)

def reactions_touching_compartment(model, compartmentid):

	csufix = "_"+compartmentid
	touching = []

	for reaction in model.getListOfReactions():
		speciesReferences = itertools.chain(reaction.getListOfProducts(), reaction.getListOfReactants())
		inCompartment = [s for s in speciesReferences if s.getSpecies().endswith(csufix)]
		if len(inCompartment) > 0:
			touching.append(reaction.getId())

	return touching

def remove_requirement(model, reactionid, speciesid):
	reaction = model.getReaction(reactionid)
	reaction.removeReactant(speciesid)


def set_standard_size(model, sizev=1.0):
	assert model

	for c in model.getListOfCompartments():
		if not c.isSetSize():
			c.setSize(sizev)


def set_species_initial_concentration(model, initial=0.0):
	assert model

	for s in model.getListOfSpecies():
		if not s.isSetInitialConcentration():
			s.setInitialConcentration(initial)


def set_gene_association(model, reactionid, gene_association):
	assert model

	reaction = model.getReaction(reactionid)
	if reaction is None:
		log("Unable to set GENE_ASSOCIATION to:"+reactionid)
	else:
		remove_gene_association(reaction)
		reaction.appendNotes("<html:p>GENE_ASSOCIATION: " + gene_association + "</html:p>")

	return


def remove_gene_association(reaction):
	if not reaction.isSetNotes():
		return

	lines = reaction.getNotesString().split("\n")
	filterGA = [l for l in lines if l.find("GENE_ASSOCIATION") == -1]
	reaction.setNotes("\n".join(filterGA))

def remove_orphan_species(model):
	removed = []
	for species in list(model.getListOfSpecies()):
		if model.getSpeciesReference(species.getId()) is None:
			removed.append(species.getId())
			species.removeFromParentAndDelete()

	return removed if len(removed) > 0 else None

def set_reversibility(model, reactionid, reversible=True):
	reaction = model.getReaction(reactionid)
	if reaction is None:
		log("Unable to set reversibility to:"+reactionid)
		return

	reaction.setReversible(reversible)

	kl = reaction.getKineticLaw()
	kl.getParameter('LOWER_BOUND').setValue(-MAX_FLOW_BOUND if reversible else 0)
	kl.getParameter('UPPER_BOUND').setValue(MAX_FLOW_BOUND)

