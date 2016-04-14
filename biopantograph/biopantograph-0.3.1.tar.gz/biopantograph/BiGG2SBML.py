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
"""bigg2sbml: add bigg elements to an existing sbml file"""

import sys
import libsbml
from collections import defaultdict

import BiGG as bigg

__author__ = "Nicolas Loira"
__email__ = "nloira@gmail.com"
__date__ = "24/July/2015"



def get_full_species_id(m):
	return str('M_' + m['bigg_id'] + '_' + m['compartment_bigg_id'])


def add_species(model, m):

	assert model
	assert m

	m_id = get_full_species_id(m)

	# check compartments
	compartment = str(m['compartment_bigg_id'])
	if model.getCompartment(compartment) is None:
		# add_compartment(model, compartment)		# DON'T!
		# move it to cytosol
		m_id = m_id[:-2] + "_c"
		compartment = "c"

		renamed_species = model.getSpecies(m_id)
		if renamed_species is not None:
			return renamed_species

	s = model.createSpecies()
	s.setCompartment(compartment)
	s.setId(m_id)
	s.setName(str(m.get('name', 'NO_NAME')))

	# let's ask bigg for additional info
	bigg_species = bigg.get_bigg_species(m['bigg_id'])

	species_notes = ""

	if 'formulae' in bigg_species:
		species_notes = ""
		for f in bigg_species['formulae']:
			species_notes += "<html:p>FORMULA: " + str(f) + "</html:p>"

		body = "<html:body>" + species_notes + "</html:body>"
		s.setNotes(body)

	return s


def add_compartment(model, compartment):
	if compartment in bigg.BIGG_COMPARTMENTS:
		newc = model.createCompartment()
		newc.setId(compartment)
		newc.setName(bigg.BIGG_COMPARTMENTS[compartment])


def add_parameter(kl, id, value):
	p = kl.createParameter()
	p.setId(id)
	p.setValue(value)
	p.setUnits("mmol_per_gDW_per_hr")
	return p


def get_reaction_results_from_any_model(biggreaction):
	"""From this generic reaction, get the reaction_results from any of the models where this reaction appears"""

	if 'models_containing_reaction' not in biggreaction:
		return None

	anymodel_id = biggreaction['models_containing_reaction'][0]['bigg_id']
	anyreaction = bigg.get_bigg_reaction_model(biggreaction['bigg_id'], anymodel_id)

	if 'results' in anyreaction:
		return anyreaction['results'][0]
	else:
		return None


def add_reaction(model, biggreaction, gene_association=None):

	assert model is not None
	assert biggreaction is not None
	subsystem = None

	# create reaction
	r = model.createReaction()
	r.setId("R_" + str(biggreaction['bigg_id']))
	r.setName(str(biggreaction['name']))

	# inherit constraints from model
	if 'results' in biggreaction:
		reaction_results = biggreaction['results'][0]
	else:
		reaction_results = get_reaction_results_from_any_model(biggreaction)

	if reaction_results is not None:
		lb = reaction_results['lower_bound']
		ub = reaction_results['upper_bound']
		# oc = reaction_results['objective_coefficient']
		subsystem = reaction_results.get('subsystem', None)

		r.setReversible(lb < 0)

		kl = r.createKineticLaw()
		add_parameter(kl, 'LOWER_BOUND', lb)
		add_parameter(kl, 'UPPER_BOUND', ub)
		add_parameter(kl, 'OBJECTIVE_COEFFICIENT', 0.0)
		add_parameter(kl, 'FLUX_VALUE', 0.0)
		kl.setFormula(" FLUX_VALUE ")

	# add new metabolites from reactant/products
	for m in biggreaction['metabolites']:

		m_id = get_full_species_id(m)
		species = model.getSpecies(m_id)
		if species is None:
			species = add_species(model, m)

		stoichiometry = m['stoichiometry']
		if stoichiometry > 0:
			s = r.createReactant()
		else:
			s = r.createProduct()

		s.setStoichiometry(abs(stoichiometry))
		s.setSpecies(species.getId())

	# add gene association and subsystem
	notes = ""
	if gene_association is not None:
		notes += "<html:p>GENE_ASSOCIATION: " + gene_association + "</html:p>"

	if subsystem is not None:
		notes += "<html:p>SUBSYSTEM: " + subsystem + "</html:p>"

	# add notes to reaction
	if notes != "":
		body = "<html:body>" + str(notes) + "</html:body>"
		r.setNotes(body)

	return r


