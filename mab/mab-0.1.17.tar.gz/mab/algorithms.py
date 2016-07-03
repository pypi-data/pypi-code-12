# /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Various MAB algorithms.
"""

import math
import random as rndm
import numpy as np
from utils import *

class MAB_Algorithm(object):
    """Base class for MAB algorithms"""
    def __init__(self, arms, history, name='General MAB Algorithm'):
        """constructor
        Args:
            arms: list of Arms
            history: 2D list
        """
        self.name = name
        self.history = History(history)
        self.init_history = History(history)
        self.num_arms = len(self.history.history)
        self.arms = arms

    def update_status(self, diff_history):
        """Just a stub method. Use update_status() of each algorithm."""
        pass

    def reset(self, arms):
        self.history = self.init_history
        self.num_arms = len(self.history.history)
        self.arms = arms

    def bulk_update_status(self, history):
        """Just a stub method. Use bulk_update_status() of each algorithm."""
        pass

    def next_choice(self, dry=False):
        """Just a stub method. Use next_choice() of each algorithm."""
        pass

    def pick(self, dry=False):
        """Play the picked arm."""
        pick = self.next_choice()
        reward = self.arms[pick].pick()
        self.history.update(pick, reward)
        return pick, reward

class Oracle(MAB_Algorithm):
    """Always picks the best arm for each round."""
    def __init__(self, arms, history, results, name='Oracle'):
        MAB_Algorithm.__init__(self, arms, history, name=name)
        self.results = History(results)
        self.pointers = [0 for _ in range(0, self.num_arms)]

    def next_choice(self):
        """Pick the best arm for the round."""
        candidates = {str(arm): self.results.history[arm][self.pointers[arm]] for arm, _ in enumerate(self.pointers)}
        pick = max(candidates.iteritems(), key=operator.itemgetter(1))[0]
        return int(pick)

    def pick(self, dry=False):
        pick = self.next_choice()
        reward = self.results.history[pick][self.pointers[pick]]
        self.pointers = [pointer+1 for pointer in self.pointers]
        self.history.update(pick, reward)
        return pick, reward

class Random(MAB_Algorithm):
    """Picks a ramdom arm."""
    def __init__(self, arms, history, name='Random'):
        MAB_Algorithm.__init__(self, arms, history, name=name)

    def next_choice(self):
        """Picks a ramdom arm."""
        pick = np.random.choice(self.num_arms, 1)[0]
        return pick

class Epsilon_First(MAB_Algorithm):
    """Epsilon-First algorithm."""
    def __init__(self, arms, history, plays, epsilon=0.05, name='Epsilon First'):
        """
        Args:
            plays: number of total plays
            epsilon: epsilon
        """
        MAB_Algorithm.__init__(self, arms, history, name=name)
        self.epsilon = epsilon
        self.plays = plays
        self.explorations = int(float(plays)*float(epsilon))
        self.plays_counter = 0

    def next_choice(self):
        """
        Randomly pick an arm for exploration.
        Pick the best arm for exploitation.
        """
        if self.plays_counter < self.explorations:
            pick = np.random.choice(self.num_arms, 1)[0]
        else:
            pick = self.history.get_best_arm()

        self.plays_counter += 1

        return pick

class Epsilon_Greedy(MAB_Algorithm):
    """Epsilon-Greedy algorithm."""
    def __init__(self, arms, history, epsilon=0.12, name='Epsilon Greedy'):
        """
        Args:
            epsilon: epsilon
        """
        MAB_Algorithm.__init__(self, arms, history, name=name)
        self.epsilon = epsilon

    def next_choice(self):
        """
        Pick the best for probability epsilon.
        Randomly pick from rest of arms for probability 1-epsilon
        """
        probabilities = [None for _ in self.arms]
        best = self.history.get_best_arm()
        others = [None for _ in self.arms]
        for i in range(0, len(self.arms)):
            if i == best:
                probabilities[i] = 1.0 - self.epsilon + self.epsilon/float(len(self.arms))
            else:
                probabilities[i] = self.epsilon/float(len(self.arms))

        return pick_by_probability(probabilities)

class Softmax(MAB_Algorithm):
    """Boltzmann Exploration (Softmax) algorithm."""
    def __init__(self, arms, history, tau=0.05, name='Softmax'):
        """
        Args:
            tau: tau
        """
        MAB_Algorithm.__init__(self, arms, history, name=name)
        self.tau = tau

    def next_choice(self):
        unknown_arm = self.history.get_unknown_arm()
        if unknown_arm is None:
            estimated_means = self.history.get_estimated_means()
            divider = sum([math.exp(estimated_mean/self.tau) for estimated_mean in estimated_means])
            probabilities = [math.exp(estimated_mean/self.tau)/divider for estimated_mean in estimated_means]
            pick = pick_by_probability(probabilities)
        else:
            pick = unknown_arm
        return pick

class UCB(MAB_Algorithm):
    """Upper Confidence Bound algorithm."""
    def __init__(self, arms, history, name='UCB'):
        MAB_Algorithm.__init__(self, arms, history, name=name)

    def next_choice(self):
        unknown_arm = self.history.get_unknown_arm()
        if unknown_arm is None:
            estimated_means = self.history.get_estimated_means()
            plays = self.history.get_plays()
            rounds_count = self.history.get_rounds_so_far()

            evaluations = [estimated_means[arm] + math.sqrt(2.0*math.log(float(rounds_count))/float(plays[arm])) for arm in range(0, len(self.arms))]
            pick = evaluations.index(max(evaluations))
        else:
            pick = unknown_arm
        return pick

class Single_Arm(MAB_Algorithm):
    """Keep choosing single arm."""
    def __init__(self, arms, history, designated_arm, name='Single Arm'):
        """
        Args:
            designated_arm: arm to pick everytime
        """
        MAB_Algorithm.__init__(self, arms, history, name=name)
        self.designated_arm = designated_arm
        if self.arms[self.designated_arm].label:
            self.name = name + '(%s)' % self.arms[self.designated_arm].label
        else:
            self.name = name

    def next_choice(self):
        return self.designated_arm

def pick_by_probability(probabilities):
    r = rndm.random()
    pick = None
    for idx, p in enumerate(probabilities):
        r -= p
        if r <= 0.0:
            pick = idx
            break
    return pick
