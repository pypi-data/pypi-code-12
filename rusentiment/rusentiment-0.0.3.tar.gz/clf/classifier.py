# -*- coding: utf-8 -*-
from collections import Counter

__author__ = 'sergeysmetanin'

import os.path
import pickle
import numpy as np

class MultinominalNB:
    def __init__(self, directory=None):
        if directory is not None:
            self._classes = self.__read_from_file(directory+'_classes.txt')
            self._priors = self.__read_from_file(directory+'_priors.txt')
            self._p_log = {label: self.__read_from_file(directory+'_p_log_' + label + '.txt') for label in self._classes }
            #self._stop_list = self.__read_list(directory+'_stop_words_lemmas.txt')

    def fit(self, samples, labels, features, freq=None, priors=None):
        self._classes = list(set(labels))
        if freq is None:
            freq = np.array([[sum([count for j, count in enumerate(samples[:, i]) if labels[j] == label])
                              for i in xrange(samples.shape[1])] for label in self._classes], dtype=np.float32)
        if priors is None:
            self._priors = np.array([sum([label == self._classes[i] for label in labels])
                                     for i in xrange(len(self._classes))], dtype=np.float32) / len(labels)
        else:
            self._priors = priors
        freq = freq.T
        p_log = np.log(freq + 1) - np.log(len(features) + sum(freq))
        p_log = p_log.T
        self._p_log = {label: {feature: p_log[i][j] for j, feature in enumerate(features)} for i, label in
                       enumerate(self._classes)}

    def __inverse_label(self, label):
        print label
        i = self._classes.index(label)
        #print self._classes[(i+1) % len(self._classes)]
        return self._classes[(i+1) % len(self._classes)]

    def proba_log(self, x, inverse):
        counter = Counter(x)
        return [sum([0 if X not in self._p_log[label if not inverse[i] else self.__inverse_label(label)] else counter[X] * self._p_log[label if not inverse[i] else self.__inverse_label(label)][X] for i, X in enumerate(counter)]) for
                label in self._classes]

    def proba(self, x):
        counter = Counter(x)
        proba = np.exp(
            [sum([0 if X not in self._p_log[label] else counter[X] * self._p_log[label][X] for X in counter]) for label
             in self._classes])
        return proba / max(proba)

    def predict(self, x, inverse):
        return self._classes[np.argmax(self.proba_log(x, inverse))]

    def score(self, x, y):
        return float(sum([self.predict(x[i]) == y[i] for i in xrange(len(x))])) / len(x)

    def save(self):
        self.__save_to_file('_classes.txt', self._classes)
        self.__save_to_file('_priors.txt', self._priors)
        for label in self._classes:
            self.__save_to_file('_p_log_' + label + '.txt', self._p_log[label])

    @staticmethod
    def __save_to_file(file_name, d):
        output = open(file_name, 'w')
        pickle.dump(d, output)
        output.close()

    @staticmethod
    def __read_from_file(file_name):
        pkl_file = open(os.path.dirname(__file__) +'/'+file_name, 'r')
        d = pickle.load(pkl_file)
        pkl_file.close()
        return d

    @staticmethod
    def __read_list(file_name):
        list_file = open(os.path.dirname(__file__) +'/'+file_name, 'r')
        return [word.replace('\n','') for word in list_file]


