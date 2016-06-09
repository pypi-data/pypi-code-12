#!/usr/bin/env python
#Once upon a time...

import random
from numpy import mean,std,log
import time
import sys
from  multiprocessing import Pool,freeze_support
from functools import partial
from itertools import izip

######################################################################
##
##      Given the ratio of F1 (complete) reads to F2 (boundary) reads
##		simulate to find the average TL that gave the ratio 
##
##      Author: jhrf
##
######################################################################

class LengthEstimator(object):
	def __init__(self,insert_mu,insert_sigma,
					complete,boundary,
					read_len=100):

		self._insert_mu = insert_mu
		self._insert_sigma = insert_sigma

		self._obs_total = complete + boundary #observed total
		self._read_thresh = int(self._obs_total * 0.0001)

		self._complete = complete 
		self._boundary = boundary
		self._read_len = read_len
		self._read_sim = self.__simulate_reads__

		self._get_read_len = (lambda: self._read_len)

	def start(self):
		if self._boundary <= 0 or self._complete <= 0:
			return 0
		else:
			return self.__run_sim__()

	def __run_sim__(self):
		found = False
		#tel_len = int(self._insert_mu+((float(self._complete)/self._boundary) * 200))
		tel_len = int((float(self._complete)/self._boundary) * (self._insert_mu-100))
		max_its = 5000
		its = 0

		best_result = float("inf")
		best_tel_len  = tel_len

		read_simulator = self._read_sim
		get_factor = self.__get_factor__

		start = time.time()

		#print "TARGET: %.3f" % (self._obs_total * 0.0001,)

		while(not found and its < max_its):
			sim_comp,sim_boun,invalid_reads = read_simulator(tel_len)
			#	result can be positive or negative thus 
			#	influencing elongation and shortening
			#	A negative diference (overestimate) results 
			#	in a shorter telomere length next iteration
			result = self.is_same_ratio(sim_comp,sim_boun)
			abs_result = abs(result)

			if abs_result < best_result:
				best_result = abs_result
				best_tel_len = tel_len

			if result == 0: 
				found = True
			else:
				mult = -1 if result < 0 else 1
				factor = get_factor(abs_result)
				tel_len += factor * mult
			its += 1

			# if its % 10 == 0:
			# 	print its,int(time.time()-start),"--------"
			# 	print best_tel_len,best_result
			# 	print tel_len,result

		return best_tel_len

	def __get_factor__(self,abs_result):
		total = self._obs_total

		if abs_result < (total * 0.001):
			factor = 1
		elif abs_result < (total * 0.2):
		 	factor = random.sample([1,2,2,4,25,200,500], 1)[0]
		elif abs_result < (total * 0.5):
		 	factor = random.sample([20,50,100,200,1000,2000], 1)[0]
		else:
			factor = int(log(abs_result)*300) / random.sample([1,2], 1)[0]
		return factor

	def is_same_ratio(self,comp,boun):
		difference = abs(comp - self._complete)
		if difference <= self._read_thresh:
			return 0
		else:
			return self._complete - comp

	def __simulate_reads__(self,tel_len):
		if tel_len < self._insert_mu:
			return ( int(self._complete * .50),self._boundary)

		#speedup
		is_complete = self.is_complete
		is_boundary = self.is_boundary

		insert_mean = self._insert_mu
		insert_sigma = self._insert_sigma

		obs_total = self._obs_total
		#speedup

		est_complete = 0
		est_boundary = 0
		invalid_read = 0
		total = 0

		while total < (obs_total):
			insert_size = (random.gauss(insert_mean,insert_sigma))
			location = random.randint(0,tel_len)
			if is_complete(location,insert_size):
				est_complete += 1
				total += 1
			elif is_boundary(location,insert_size):
				est_boundary += 1
				total += 1
			else:
				invalid_read += 1

		return (est_complete,est_boundary,invalid_read)

	def is_complete(self,location,insert_size):
		return (location - insert_size) > 0

	def is_boundary(self,location,insert_size):
		return (location - self._get_read_len()) > 0

def check_results(sim_results):
	if 0 in sim_results:
		sys.stderr.write("[WARNING] Telomere length reported zero. This means telomercat\n"+
						"\tfailed to identify enough complete or boundary reads.\n"+
						"\tThis  may mean your original sample was preprocessed to remove \n"+
						"\ttelomere reads. Alternatively this sample could have \n"+
						"\tvery short average TL.\n")

def run_simulator(insert_mu,insert_sigma,complete,boundary,proc,read_len,N=10):
	simmer = LengthEstimator(insert_mu,insert_sigma,complete,boundary,read_len)
	res = []
	invalid_count = []
	for i in range(N):
		length,invalid = simmer.start()
		res.append(length)
		invalid_count.append(invalid)

	check_results(res)
	print mean(invalid_count)
	return (mean(res),std(res))

def estimator_process(job,insert_mu,insert_sigma,complete,boundary,read_len):
	length_estimator = LengthEstimator(insert_mu,insert_sigma,complete,boundary,read_len)
	results = length_estimator.start()
	return results

def run_simulator_par(insert_mu,insert_sigma,complete,
					  boundary,proc,read_len,N=10):

	freeze_support()
	p = Pool(proc)
	sim_partial = partial(estimator_process,insert_mu=insert_mu,
						  insert_sigma=insert_sigma,complete=complete,
						  boundary=boundary,read_len=read_len)

	results = p.map(sim_partial,range(N))
	p.close()
	check_results(results)
	return (mean(results),std(results))

if __name__ == "__main__":
	#print run_simulator_par(265, 83, 7781, 265, 16, 100,N=1)
	#print run_simulator(404, 0, 54247, 3121, 16, 100,N=1)

	#print run_simulator(265, 0, 53500,1668, 16, 100,N=1)
	print "Type telomerecat into your terminal for more details"