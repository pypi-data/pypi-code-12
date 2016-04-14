#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import sys
import os

from collections import defaultdict
import pprint
import time
# import cPickle as pickle
try:
	import cPickle as pickle
except:
	import pickle


"""bigglib: extract, using BiGG 2.0 API, information about reactions,
the models that contain the reactions, the associated genomes,
the associated genes, and gene association formula.
Uses an external cache file whenever possible."""

__author__ = "Nicolas Loira"
__email__ = "nloira@gmail.com"
__date__ = "14/July/2015"

BIGG_REACTION_INFO = 'http://bigg.ucsd.edu/api/v2/universal/reactions/%s'
BIGG_MODEL_INFO = 'http://bigg.ucsd.edu/api/v2/models/%s'
BIGG_REACTION_IN_MODEL = 'http://bigg.ucsd.edu/api/v2/models/%s/reactions/%s'
BIGG_METABOLITE_INFO = 'http://bigg.ucsd.edu/api/v2/universal/metabolites/%s'
BIGG_QUERY_REACTION = 'http://bigg.ucsd.edu/api/v2/search?query=%s&search_type=reactions'

BIGG_WAIT = 0.3

BIGG_COMPARTMENTS = {
	'c': 'cytosol',
	'p': 'periplasm',
	'e': 'extracellular space',
	'x': 'peroxisome',
	'm': 'mitochondria',
	'n': 'nucleus',
	'r': 'endoplasmic reticulum',
	'x': 'peroxisome/glyoxysome',
	'l': 'lysosome',
	'g': 'golgi apparatus',
	'n': 'nucleus',
	'f': 'flagellum',
	's': 'eyespot',
	'h': 'chloroplast',
	'u': 'thylakoid',
	'v': 'vacuole'}


cache = dict()
dirtycache = False
CACHE_FILE = os.path.expanduser("~/.bigg_cache.pkl")
disable_cache = False


def get_bigg_json(req):

	global cache
	global dirtycache

	if req in cache:
		return cache[req]

	results = None
	r = None

	log("Requesting to BiGG: [%s]" % req)
	try:
		r = requests.get(req)
		results = r.json()
	except Exception as e:
		if r is None:
			log("Error (%s) (%s) -- No response for request!" % (str(e), req))
		else:
			log("Error (%s) (%s) -- No json from payload:\n%s" % (str(e), req, r.text))
		results = None

	time.sleep(BIGG_WAIT)
	cache[req] = results
	dirtycache = True

	return results


def get_bigg_reaction(reactionid):

	results = get_bigg_json(BIGG_REACTION_INFO % reactionid)

	return results


def get_bigg_species(speciesid):

	results = get_bigg_json(BIGG_METABOLITE_INFO % speciesid)

	return results


def guess_reaction(reactionid):
	results = get_bigg_json(BIGG_QUERY_REACTION % reactionid)

	if results['results_count'] > 0:
		for r in results['results']:
			candidate_reaction = get_bigg_reaction(r['bigg_id'])
			if candidate_reaction is not None and 'old_identifiers' in candidate_reaction:
				if reactionid in candidate_reaction['old_identifiers']:
					return candidate_reaction

	return None


def extract_model2genomes_from_reaction(biggreaction):

	models = [m['bigg_id'] for m in biggreaction['models_containing_reaction']]

	model2genome = dict()

	for model in models:
		results2 = get_bigg_json(BIGG_MODEL_INFO % model)
		model2genome[model] = results2["genome_name"]

	return model2genome


def extract_model2ga_from_reaction(biggreaction):

	models = [m['bigg_id'] for m in biggreaction['models_containing_reaction']]

	reactionid = biggreaction['bigg_id']

	# get reaction per model
	reactionXmodel2ga = defaultdict(dict)
	reactionXmodel2genes = defaultdict(dict)

	for model in models:
		results = get_bigg_json(BIGG_REACTION_IN_MODEL % (model, reactionid))
		reactionXmodel2ga[reactionid][model] = results["results"][0]["gene_reaction_rule"]
		all_genes = results["results"][0]["genes"]
		reactionXmodel2genes[reactionid][model] = [g['bigg_id'] for g in all_genes]

	return (reactionXmodel2ga, reactionXmodel2genes)


def get_bigg_reaction_model(reactionid, modelid):
	# log("Requesting %s in model %s" % (reactionid, modelid))
	reaction_info = get_bigg_json(BIGG_REACTION_IN_MODEL % (modelid, reactionid))

	return reaction_info


def log(msg):
	"""Write to stderr"""
	sys.stderr.write(msg + '\n')


def testBIGGrm():
	r = get_bigg_reaction_model('PMI12346PH', 'iMM1415')
	pprint.pprint(r)


def testBIGG():
	x = get_bigg_reaction('PMI12346PH')
	pprint.pprint(x)

	x = get_bigg_reaction('CFAS160E')
	pprint.pprint(x)

	x = get_bigg_reaction('PMI12346PH')
	pprint.pprint(x)


def close():
	update_cache()


def update_cache():
	global cache
	global dirtycache

	if disable_cache:
		return

	if dirtycache:
		# log("/\ Updating cache...")
		with open(CACHE_FILE, 'wb') as cachefd:
			pickle.dump(cache, cachefd, -1)
		dirtycache = False
	else:
		pass
		# log("/\ Cache is clean")


def init(usecache=True):

	global disable_cache

	if usecache:
		init_cache()
	else:
		disable_cache = True


def init_cache():
	global cache

	# if there is a cache file, use it!
	if os.path.isfile(CACHE_FILE):
		with open(CACHE_FILE, 'rb') as cachefd:
			cache = pickle.load(cachefd)
