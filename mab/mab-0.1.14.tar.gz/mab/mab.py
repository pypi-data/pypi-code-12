# /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Multi-Armed Bandits agent.
"""

from algorithms import *
from utils import *

class MAB(object):
    """
    Agent class representing MAB player.
    """
    def __init__(self):
        self.arms = []
        self.history = History([])

    def add_auto_generated_arms(self, num_arms, labels=None):
        self.arms += [Arm(label="Arm-%s" % (len(self.arms)+i)) for i in range(0, num_arms)]
        for _ in range(0, num_arms):
            self.history.add_arm([])

    def add_arm(self, dist_type='nd', label=None, mean=None, sd=None, truncate=[0.0, 1.0]):
        self.arms.append(Arm(dist_type=dist_type, label=label, mean=mean, sd=sd, truncate=truncate))
        self.history.add_arm([])

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def play(self):
        pick, reward = self.algorithm.pick()

    def summary(self):
        summary = {}
        summary['algorithm'] = self.algorithm.name
        summary['rounds'] = self.history.get_rounds_so_far()
        summary['true_means'] = [arm.mean for arm in self.algorithm.arms]
        summary['true_sds'] = [arm.sd for arm in self.algorithm.arms]
        summary['empirical_means'] = self.history.get_means()
        summary['empirical_sds'] = self.history.get_sds()
        summary['regret'] = self.calc_regret()
        summary['total_reward'] = self.history.get_total_reward()
        summary['plays'] = [len(hist_of_arm) for hist_of_arm in self.history.get_dense_history()]
        return summary

    def calc_regret(self):
        # Compare to Oracle
        oracle = MAB()
        results = [[arm.pick() for _ in range(0, self.history.get_rounds_so_far())] for arm in self.arms]
        for arm in self.arms:
            oracle.add_arm(label=arm.label, mean=arm.mean, sd=arm.sd, truncate=arm.truncate)
        oracle.set_algorithm(Oracle(arms=self.arms, history=oracle.history.history, results=results))
        for _ in range(0, self.history.get_rounds_so_far()):
            oracle.play()

        oracle_total_reward = oracle.history.get_total_reward()
        total_reward = self.history.get_total_reward()
        regret = oracle_total_reward - total_reward
        return regret

class Simulated_MAB(MAB):
    def __init__(self, rounds):
        MAB.__init__(self)
        self.rounds = rounds

    def add_auto_generated_arms(self, num_arms, labels=None):
        self.arms += [Simulated_Arm(self.rounds, label="Arm-%s" % (len(self.arms)+i)) for i in range(0, num_arms)]
        for _ in range(0, num_arms):
            self.history.add_arm([])

    def add_arm(self, dist_type='nd', label=None, mean=None, sd=None, truncate=[0.0, 1.0]):
        self.arms.append(Simulated_Arm(self.rounds, dist_type=dist_type, label=label, mean=mean, sd=sd, truncate=truncate))
        self.history.add_arm([])

    def reset(self, dry=True):
        self.history = History([])
        for arm in self.arms:
            arm.reset()
        self.algorithm.reset(arms)

    def calc_regret(self):
        # Compare to Oracle
        oracle = Simulated_MAB(self.history.get_rounds_so_far())
        # results = [[arm.pick() for _ in range(0, self.history.get_rounds_so_far())] for arm in self.arms]
        results = [arm.results for arm in self.arms]
        for arm in self.arms:
            oracle.add_arm(label=arm.label, mean=arm.mean, sd=arm.sd, truncate=arm.truncate)
        for idx, arm in enumerate(oracle.arms):
            arm.force_update_results([results[idx]])
        oracle.set_algorithm(Oracle(arms=self.arms, history=oracle.history.history, results=results))
        for _ in range(0, self.history.get_rounds_so_far()):
            oracle.play()

        oracle_total_reward = oracle.history.get_total_reward()
        total_reward = self.history.get_total_reward()
        regret = oracle_total_reward - total_reward
        return regret

class InvalidSettingException(Exception):
    """
    Exception for invalid settings of Arm
    """
    def __init(self, msg='Failed to update history.'):
        Exception.__init__(self, msg)
