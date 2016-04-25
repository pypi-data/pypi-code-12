import re
from django.db import models
WORD_SCORES = [0, 0, 0.1, 0.1, 0.2, 0.3, 0.5, 0.8, 1, 1.2, 1.5, 2, 2.5, 3.2]

def content_score(text):
    """Computes a score intended to correlate with the amount of
    information conveyed by a block of prose."""

    score = 0
    word_counts = {}        # keep track of the words seen so we can penalise repetitiveness
    for w in re.split(r'\s+', text.lower()):
        try:
            wscore = WORD_SCORES[len(w)]
        except IndexError:
            wscore = WORD_SCORES[-1]

        wc = word_counts.get(w, 1)
        score += wscore / wc
        word_counts[w] = wc + 1

    return score


class StringAttributeScorer(object):
    def __init__(self, target, max_score):
        self.target = target
        self.max_score = max_score

    def get_score(self, inst):
        try:
            s = content_score(getattr(inst, self.name))
        except AttributeError:
            return 0

        return min(s, self.target)/float(self.target) * self.max_score

    def get_max_score(self):
        return self.max_score


class HasAttributeScorer(object):
    def __init__(self, score):
        self.score = score

    def get_score(self, inst):
        if getattr(inst, self.name, None):
            return self.score
        return 0

    def get_max_score(self):
        return self.score


class CollectionLengthScorer(object):
    def __init__(self, scores):
        self.scores = scores

    def get_score(self, inst):
        """Most of this implementation is concerned with
        trying all possible routes to getting a number of
        items to score. We accept:

        - Django Managers/QuerySets (anything with a .count() method)
        - collections (anything with a __len__ method)
        - zero-argument callables that return either of the above

        """
        att = getattr(inst, self.name, None)
        if att is None:
            return 0
        if isinstance(att, models.Manager):
            c = att.count()
        elif hasattr(att, '__len__'):
            c = len(att)
        elif hasattr(att, '__call__'):
            try:
                res = att()
            except AttributeError:
                return 0
            else:
                if isinstance(res, models.query.QuerySet):
                    c = res.count()
                elif hasattr(res, '__len__'):
                    c = len(res)
        else:
            return 0

        try:
            return self.scores[c]
        except IndexError:
            return self.scores[-1]

    def get_max_score(self):
        return max(self.scores)


class DeclarativeScoreSystem(type):
    """Metaclass that allows an ObjectScorer subclass to have its list of
    scorers defined in a Python class definition rather than by assigning
    to self.scorers.

    Also assigns the name attribute on scorers so they can find which
    attribute to inspect."""

    def __new__(cls, name, bases, attrs):
        scorers = []
        for n in attrs:
            s = attrs[n]
            if hasattr(s, 'get_score'):
                s.name = n
                scorers.append(s)
        attrs['scorers'] = scorers
        return type.__new__(cls, name, bases, attrs)


class ObjectScorer(object):
    __metaclass__ = DeclarativeScoreSystem

    def get_score(self, inst):
        score = sum([s.get_score(inst) for s in self.scorers])
        max_score = sum([s.get_max_score() for s in self.scorers])
        other_scores, max_other_scores = self.other_scores(inst, score)
        return int(float(score + other_scores) * 100.0/float(max_score + max_other_scores) + 0.5)

    def other_scores(self, inst, score):
        """Returns a tuple (score, max_score) representing non-declarative scores"""
        return (0, 0)
