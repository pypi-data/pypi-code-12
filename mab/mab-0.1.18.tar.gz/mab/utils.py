# /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Utility classes.
"""

import operator
import math
import numpy as np

DEFAULT_MEAN_OF_SD = 0.3
DEFAULT_SD_OF_SD = 0.05
DEFAULT_MEAN_OF_MEAN = 0.5
DEFAULT_SD_OF_MEAN = 0.1

class History(object):
    """
    Class for choice history and all true results(used for simulation).
    """
    def __init__(self, hist):
        """N x M list of past choices
        N: Number of arms
        M: Number of rounds
        history[n][m] is float value only if arm n was picked at round m.
        """
        is_hist_list = isinstance(hist, list)
        is_hist_of_every_arm_list = all([isinstance(hist_of_arm, list) for hist_of_arm in hist])
        is_all_float_or_none = all([element is None or isinstance(element, float) for arm in hist for element in arm])
        is_size_valid = all([len(hist[i]) == len(hist[i-1]) for i in range(0, len(hist))])
        if is_hist_list and is_hist_of_every_arm_list and is_all_float_or_none and is_size_valid:
            self.history = hist
        else:
            raise InvalidHistoryException()

    def reset(self):
        new_history = [[] for _ in self.history]
        self.history = new_history

    def update(self, index_arm, value):
        """
        Update history of a designated arm with given value.
        """
        if isinstance(value, float):
            for i in range(0, len(self.history)):
                if index_arm == i:
                    self.history[index_arm].append(value)
                else:
                    self.history[i].append(None)
        else:
            raise UpdateFailedException()

    def add_arm(self, hist_of_arm, index=None):
        self.history.append(hist_of_arm)

    def get_unknown_arm(self):
        unknown = None
        for idx, hist_of_arm in enumerate(self.get_dense_history()):
            if len(hist_of_arm) == 0:
                unknown = idx
                break
        return unknown

    def get_best_arm(self):
        estimated_means = self.get_estimated_means()
        candidates = {str(idx): estimated_mean for idx, estimated_mean in enumerate(estimated_means)}
        best = int(max(candidates.iteritems(), key=operator.itemgetter(1))[0])
        return best

    def get_estimated_means(self):
        dense_history = self.get_dense_history()
        estimated_means = [float(sum(hist_of_arm))/float(len(hist_of_arm)) if len(hist_of_arm)>0 else 0.0 for hist_of_arm in dense_history]
        return estimated_means

    def get_dense_history(self):
        """
        Remove None elements from history.
        """
        dense_history = []
        for hist_of_arm in self.history:
            dense_history.append([element for element in hist_of_arm if element is not None])
        return dense_history

    def get_rounds_so_far(self):
        return len(self.history[0])

    def get_plays(self):
        return [len(hist_of_arm) for hist_of_arm in self.get_dense_history()]

    def get_total_rewards(self):
        return [sum(hist_of_arm) for hist_of_arm in self.get_dense_history()]

    def get_total_reward(self):
        return sum(self.get_total_rewards())

    def get_means(self):
        plays = self.get_plays()
        total_rewards = self.get_total_rewards()
        return [float(total_reward)/float(play) if play>0 else 0.0 for total_reward, play in zip(total_rewards, plays)]

    def get_sds(self):
        plays = self.get_plays()
        means = self.get_means()
        variances = [sum([(mean-reward)**2.0 for reward in hist_of_arm])/float(play) if play>0 else 0.0 for mean, hist_of_arm, play in zip(means, self.get_dense_history(), plays)]
        sds = [math.sqrt(variance) for variance in variances]
        return sds

class Arm(object):
    """
    Arm class representing each arm.
    """
    def __init__(self, dist_type='nd', label=None, mean=None, sd=None, truncate=[0.0, 1.0]):
        self.mean = mean
        self.sd = sd
        self.label = label
        self.truncate = truncate
        while self.sd is None:
            self.sd = sd or np.random.normal(DEFAULT_MEAN_OF_SD, DEFAULT_SD_OF_SD, 1)[0]
        while self.mean is None or self.mean > self.truncate[1] or self.mean < self.truncate[0]:
            self.mean = mean or np.random.normal(DEFAULT_MEAN_OF_MEAN, DEFAULT_SD_OF_MEAN, 1)[0]

    def update_label(self, label):
        self.label = label

    def pick(self):
        """
        Return a reward from distribution.
        """
        reward = None
        is_valid_value = (reward >= self.truncate[0] or reward <= self.truncate[1])
        while reward is None or not is_valid_value:
            reward = np.random.normal(self.mean, self.sd, 1)[0]
        return reward

class Simulated_Arm(Arm):
    """
    Simulated_Arm class representing each arm with fixed results.
    """
    def __init__(self, size, dist_type='nd', label=None, mean=None, sd=None, truncate=[0.0, 1.0]):
        Arm.__init__(self, dist_type='nd', label=label, mean=mean, sd=sd, truncate=truncate)
        self.size = size
        self.pointer = 0

        self.results = []
        while len(self.results) < self.size:
            reward = np.random.normal(self.mean, self.sd, 1)[0]
            if reward >= 0.0 and reward <= 1.0:
                self.results.append(reward)

    def reset(self, dry=True):
        self.pointer = 0
        # if not dry:
        self.results = []
        while len(self.results) < self.size:
            reward = np.random.normal(self.mean, self.sd, 1)[0]
            if reward >= 0.0 and reward <= 1.0:
                self.results.append(reward)

    def update_state(self):
        self.pointer += 1

    def force_update_results(self, results):
        self.results = results

    def pick(self):
        """
        Return a reward from results list.
        """
        if self.pointer >= self.size:
            reward = None
        else:
            reward = self.results[self.pointer]
            self.pointer += 1
        return reward

class InvalidHistoryException(Exception):
    """
    Exception for invalid values or type of history.
    """
    def __init__(self, msg='Invalid history.'):
        Exception.__init__(self, msg)

class UpdateFailedException(Exception):
    """
    Exception for invalid use of update()
    """
    def __init(self, msg='Failed to update history.'):
        Exception.__init__(self, msg)
