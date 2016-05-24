# -*- coding: utf-8 -*-
#
#   This file belongs to the MURDOCK project
#
#   Copyright (C) 2013 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
Module :mod:`murdock.search.search`
-----------------------------------

Specifies the Murdock conformational search API :class:`Search`. A list of
implemented search modules is given :mod:`here <murdock.search`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import json
import logging
import os

import numpy

import murdock.config
import murdock.misc


log = logging.getLogger('search')


class SearchError(Exception):
    pass


class Search(object):
    """Parent class for all search algorithms.

    The class is supposed to hold all properties and methods commomly needed by
    all search algorithms. So far, it is only used to initialize the list of
    :class:`~murdock.transforms.Transformation` instances which can be modified
    by search algorithms.

    """

    def __init__(
            self, docking, root, scoring, parms=None, name='unnamed',
            debugsampling=False, intvideo=None, extvideo=None,
            store_decoy_scores=False):
        #: :class:`~murdock.runner.docking.Docking` assosiated with this search
        self.docking = docking
        #: current iteration step
        self.iteration = 0
        #: name of this :class:`Search` instance
        self.name = name
        #: root :class:`~murdock.tree.Node` of the structure modified during
        #: the search
        self.root = root
        #: reference to the scoring function to be used
        self.scoring = scoring
        #: dictionary of individual search parameters
        self.parms = parms
        #: wether to store all :attr:`state()` values for sampling analysis
        self.debugsampling = debugsampling
        #: last reported total score (used to log scoring improvements)
        self.last_reported_tot = None
        #: internal video of this single search
        self.intvideo = intvideo
        #: external video this search can add objects and frames to
        self.extvideo = extvideo
        #: wether to store the score of every single state sampled
        self.store_decoy_scores = store_decoy_scores
        #: dictionary of search scoring histories
        self.scoring_hist = {}
        # Initialize result file sections storing intermediate scoring values.
        self.init_scoring_history()
        if self.store_decoy_scores:
            self.init_scoring_history(
                label='decoys', total=False, weighted=False,
                unweighted=True)

    def add_score_to_history(
            self, scoring, label='search', total=True, weighted=True,
            unweighted=False):
        """Add scoring values to the scoring history.

        Check :meth:`init_scoring_history` for details.

        """
        sdict = self.scoring_hist[label]
        sdict['iterations'].append(self.iteration)
        if total:
            sdict['total'].append(scoring.total())
        if weighted:
            for term in scoring.terms:
                sdict['terms']['weighted'][term.name].append(term.weighted())
        if unweighted:
            for term in scoring.terms:
                sdict['terms']['unweighted'][term.name].append(
                    term.unweighted())
        return True

    def check_distance(self, root, maxdist):
        """Return wether a max. distance between molecules has been reached.

        This criterion cat be used to abort diverging docking runs before the
        maximum number of iterations has been reached.

        """
        for child1 in root.children:
            for child2 in root.children:
                if child1 is child2:
                    continue
                dist = numpy.linalg.norm(
                    child1.atoms[0].coords - child2.atoms[0].coords)
                if dist > maxdist:
                    log.warning(
                        'The distance between two atoms in `%s` and `%s` has '
                        'reached %d A.', child1.name, child2.name, dist)
                    return True
        return False

    def check_scoring_interrupt(self, it_before_check):
        """Return wether the score after a number of iterations is still < 0.

        After `niterations`, check wether the score is still > 0 (which
        usually means no binding conformation has been found yet). This
        criterion can be used to abort diverging docking runs before the
        maximum number of iterations has been reached.

        """
        if self.iteration >= it_before_check and self.scoring.total() > 0:
            log.warning(
                'The score after %d iterations is still > 0.', self.iteration)
            return True
        return False

    def init_scoring_history(
            self, label='search', total=True, weighted=True,
            unweighted=False):
        """Create a JSON file to store a scoring history.

        After this method has been called once during the search setup, the
        method :meth:`add_score_to_history()` can be called (e.g. after each
        search iteration) to store the current scoring values (or the best
        found scoring values).

        """
        if label in self.scoring_hist:
            raise SearchError(
                'If the method `init_scoring_history()` is called more than '
                'once during a search, the parameter `label` must be '
                'different each time. The label `%s` already exists.' % label)
        self.scoring_hist[label] = {}
        sdict = self.scoring_hist[label]
        sdict['iterations'] = []
        if total:
            sdict['total'] = []
        if weighted or unweighted:
            sdict['terms'] = {}
        if weighted:
            sdict['terms']['weighted'] = {
                _t.name: [] for _t in self.scoring.terms}
        if unweighted:
            sdict['terms']['unweighted'] = {
                _t.name: [] for _t in self.scoring.terms}
        return True

    def log_status(self, log_meth, score_initial, message=''):
        """Output status information during search run.
        """
        tot = self.scoring.total()
        tot_diff = tot - score_initial
        if self.last_reported_tot is None:
            diff = tot_diff
        else:
            diff = tot - self.last_reported_tot
        log_meth(
            '[%s] %6d (ITER), %.2e (DIFF), %.2e (TOT), %.2e (TOTDIFF); '
            '%s' % (self.name, self.iteration, diff, tot, tot_diff, message))
        log_meth('[%s] %s' % (self.name, ', '.join(['%s: %.2e' % (
            _term.name, _term.weighted()) for _term in self.scoring.terms])))
        self.last_reported_tot = tot
        return True

    def run(self):
        """Start search run using the child method ``search()``.
        """
        self.iteration = 0
        success = self.search()
        self.write_scoring_histories()
        return success

    def search(self):
        raise NotImplementedError

    def setup(self):
        """Setup and initialize search.

        This method is supposed to be overwritten by individual setup functions
        for each search module inheriting from :class:`Search`.

        """
        return True

    def write_scoring_histories(self):
        for label in self.scoring_hist:
            self._write_scoring_history(label)
        return True

    def _write_scoring_history(self, label):
        filepath = self.docking.get_search_filepath(label)
        if not filepath:
            return False
        hist = None
        try:
            hist = murdock.misc.load_ordered_json(filepath)
        except IOError:
            pass
        except ValueError:
            log.error(
                'The search history file `%s` is damaged and will be '
                'replaced.', filepath)
        if hist is None:
            hist = {}
        if 'runs' not in hist:
            hist['runs'] = []
        run = self.docking.current_run
        while True:
            try:
                runhist = hist['runs'][run.ind]
                break
            except IndexError:
                hist['runs'].append(collections.OrderedDict())
        step = self.docking.current_step
        if step.title in runhist:
            log.warning(
                'The file `%s` contains a search history for run %d, step %d '
                'which will now be replaced.', filepath, run.serial,
                step.serial)
        runhist[step.title] = self.scoring_hist[label]
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(hist, indent=2))
        return True


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def search(self):
        """Configuration options for the conformational search method used:

            - "module":
                search module to be used (must be compatible with the
                :mod:`~murdock.search` API) `(dtype=str, required=False)`

            - "parameters":
                parameters passed to the scoring module, e.g.
                :meth:`murdock.search.ps.ConfigDeclaration.parameters`
                `(dtype=dict, required=True)`

            - "intvideo":
                wether to create a video for each conformational
                search run, e.g. for development or presentation purposes
                `(dtype=bool, required=False, default=False)`

            - "extvideo":
                wether to create a video compiled of all search runs, e.g. for
                development or presentation purposes
                `(dtype=bool, required=False, default=False)`

            - "store_decoy_scores":
                wether to store the score of every single state sampled
                `(dtype=bool, required=False, default=False)`

        """

        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='module', dtype=Option.string, description='python module '
            'containing the conformational search function to be used'))
        opt.append(Option(
            name='parameters', dtype=dict, description='dictionary containing '
            'all parameters passed to the search function'))
        opt.append(Option(
            name='intvideo', dtype=bool, description='wether to write a video '
            'for each search run', required=False, default=False))
        opt.append(Option(
            name='extvideo', dtype=bool, description='wether to write a video '
            'compiled of all search runs', required=False, default=False))
        opt.append(Option(
            name='store_decoy_scores', dtype=bool, description='wether to '
            'store the score of every single state sampled', required=False,
            default=False))
        return opt
