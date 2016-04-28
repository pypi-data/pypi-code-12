'''
Enables fast on-demand sampling from a categorical probability distribution
'''

import numpy.random as r
import numpy as np


class MultinomialSampler(object):

	def __init__(self, scores):
		if len(scores) < 1:
			raise ValueError('The scores list must have length >= 1')
		self.scores = scores
		self.total = float(sum(scores))
		self.K = len(scores)
		self.setup()


	def get_probability(self, k):
		'''
		Get the actual probability associated to outcome k
		'''
		return self.orig_prob_mass[k]


	def setup(self):
		self.orig_prob_mass = np.zeros(self.K)
		self.mixture_prob_mass = np.zeros(self.K)
		self.mass_reasignments = np.zeros(self.K, dtype=np.int64)
 
		# Sort the data into the outcomes with probabilities
		# that are larger and smaller than 1/K.
		smaller = []
		larger  = []
		for k, score in enumerate(self.scores):
			self.orig_prob_mass[k] = score / self.total
			self.mixture_prob_mass[k] = (self.K*score) / self.total
			if self.mixture_prob_mass[k] < 1.0:
				smaller.append(k)
			else:
				larger.append(k)
 
		# We will have k different slots. Each slot represents 1/K
		# prbability mass, and to each we allocate all of the probability
		# mass from a "small" outcome, plus some probability mass from
		# a "large" outcome (enough to equal the total 1/K).
		# We keep track of the remaining mass left for the larger outcome,
		# allocating the remainder to another slot later.
		# The result is that the kth has some mass allocated to outcome
		# k, and some allocated to another outcome, recorded in J[k].
		# q[k] keeps track of how much mass belongs to outcome k, and 
		# how much belongs to outcome J[k].
		while len(smaller) > 0 and len(larger) > 0:
			small_idx = smaller.pop()
			large_idx = larger.pop()
 
			self.mass_reasignments[small_idx] = large_idx
			self.mixture_prob_mass[large_idx] = (
				self.mixture_prob_mass[large_idx] -
				(1.0 - self.mixture_prob_mass[small_idx])
			)
 
			if self.mixture_prob_mass[large_idx] < 1.0:
				smaller.append(large_idx)
			else:
				larger.append(large_idx)
 
		return self.mass_reasignments, self.mixture_prob_mass


	def sample(self, shape=()):

		if len(shape) < 1:
			return self._sample()
		else:
			this_dim = shape[0]
			recurse_shape = shape[1:]
			return np.array(
				[self.sample(recurse_shape) for i in range(this_dim)]
			, dtype='int64')


	def _sample(self):

		# Draw from the overall uniform mixture.
		k = np.int64(int(np.floor(r.rand()*self.K)))
	 
		# Draw from the binary mixture, either keeping the
		# small one, or choosing the associated larger one.
		if r.rand() < self.mixture_prob_mass[k]:
			return k
		else:
			return self.mass_reasignments[k]
 

