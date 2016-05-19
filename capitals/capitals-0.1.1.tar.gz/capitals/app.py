# coding=utf-8
# Filename: __main__.py
from __future__ import division, print_function

import random
import os
from difflib import SequenceMatcher


class Game(object):

    def __init__(self):
        self.MAX_SCORE = 10
        self.SIMILARITY_TOLERANCE = 0.75
        self.total_score = 0
        self.n_asked = 0
        self.n_correct = 0
        current_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_path, "data/capitals.txt")) as f:
            lines = f.read().splitlines()
        self.data = dict([l.split('\t') for l in lines])
        self.country_selection = self.data.keys()
        random.shuffle(self.country_selection)

    def ask_for(self, country):
        return raw_input('Was ist die Hauptstadt von {0}? '.format(country))

    def loop(self):
        for country in self.country_selection:
            answer = self.ask_for(country)
            self.n_asked += 1
            right_answer = self.data[country]
            score = self.calculate_score(answer, right_answer)
            print(score)
            if score > 0:
                self.n_correct += 1
                if abs(self.MAX_SCORE - score) < 0.001:
                    print('Richtig!')
                else:
                    print('Fast richtig! Richtige Antwort: {0}'
                          .format(right_answer))
            self.total_score += score
            self.print_status()

    def calculate_score(self, answer, right_answer):
        similarity = self.calculate_similarity(answer, right_answer)
        print(similarity)
        if similarity < self.SIMILARITY_TOLERANCE:
            return 0
        return (similarity - self.SIMILARITY_TOLERANCE) * 1. /\
            (1. - self.SIMILARITY_TOLERANCE) * self.MAX_SCORE

    def print_status(self):
        n_countries = len(self.country_selection)
        ratio = int(self.n_correct / self.n_asked * 100.)
        print('Zwischenstand: {0}/{1} ({2}) {3}%'
              .format(self.n_correct, self.n_asked, n_countries, ratio))

    def in_both(self, s1, s2):
        s1 = s1.lower()
        s2 = s2.lower()
        s1_chars = set(s1)
        s2_chars = set(s2)
        result = sorted(s1_chars.intersection(s2_chars))
        return result

    def calculate_similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()


def main():
    game = Game()
    try:
        game.loop()
    except KeyboardInterrupt:
        print('\nCiao!')


if __name__ == '__main__':
    main()
