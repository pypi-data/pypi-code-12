# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import random

import numpy

from murdock.misc import (
    float_ge_zero, float_gt_zero, int_ge_zero, int_gt_zero)
import murdock.search


log = logging.getLogger('search.mc')


class SearchMCError(Exception):
    pass


class Search(murdock.search.Search):
    """Simple Monte Carlo search.
    """

    def search(self):
        """Run Monte Carlo search.
        """
        # Initialize search.
        root = self.root.deepcopy()
        self.transforms = root.descendant_transforms()
        for tf in self.transforms:
            tf.randomize_state(tf.scaling * self.init_step)
        root.update_source()
        self.scoring.rescore()
        scoring = self.scoring.deepcopy(root=root)
        scoring.rescore()
        score_initial = scoring.total()
        if self.intvideo is not None:
            self.intvideo.add_static(root)
        # Run search.
        tfs = list(self.transforms)
        nrejected = 0
        self.iteration = 0
        for it in xrange(self.maxit):
            if self.iteration % max(1, int(self.maxit / 100)) == 0:
                temp_str = 'zero' if not self.temp else '%.2e' % self.temp
                self.log_status(
                    log.info, score_initial,
                    message='%s (TEMP), rejected: %d / %d' % (
                        temp_str, nrejected, self.max_rejected))
                self.add_score_to_history(self.scoring)
                if (self.abort_at_dist is not None and
                        self.check_distance(root, self.abort_at_dist)):
                    return False
            random.shuffle(tfs)
            accepted = False
            self.iteration += 1
            for tf in tfs:
                # Step and rescore.
                tf.randomize_velocity(tf.scaling)
                tf.step()
                s = scoring.rescore(tf.node)
                # Store degree of freedom states.
                if self.debugsampling:
                    tf.source.history.append(tf.get_fmt_state())
                if self.intvideo is not None:
                    self.intvideo.add_frame(root)
                if self.store_decoy_scores:
                    self.add_score_to_history(
                        scoring, label='decoys', total=False,
                        weighted=False, unweighted=True)
                accept = False
                if s <= 0:
                    accept = True
                elif self.temp is not None:
                    try:
                        p = 1 / (1 + numpy.exp(s / self.temp))
                        accept = random.random() < p
                    except FloatingPointError:
                        pass
                if accept:
                    # Accept last step.
                    accepted = True
                    if self.extvideo is not None:
                        self.extvideo.add_frame(root)
                    if scoring.total() < self.scoring.total():
                        root.update_source()
                        diff = self.scoring.rescore()
                        if s > 0:
                            after = self.scoring.total()
                            before = after - diff
                            raise SearchMCError(
                                'The `best state` (score = %.6f) was just '
                                'overwritten with a worse-scored state '
                                '(score = %.6f). This points to a crucial '
                                'error in the search or scoring code used.' %
                                (before, after))
                else:
                    # Reject last step.
                    tf.invert_velocity()
                    tf.step()
                    scoring.rescore(tf.node)
            if self.dtemp is not None:
                self.temp *= self.dtemp
            if accepted:
                nrejected = 0
            else:
                nrejected += 1
            if nrejected > self.max_rejected:
                log.info('%i rejected iterations in a row. Done.', nrejected)
                return True
        log.info('Maximum number of iterations (%d) reached.', self.maxit)
        self.add_score_to_history(self.scoring)
        return True

    def setup(self):
        """Setup search settings and parameters.
        """
        self.name = 'Monte Carlo'
        #: maximum amount of initial tranformations
        self.init_step = self.parms['max_init_step']
        #: current temperature
        self.temp = None
        try:
            self.temp = self.parms['initial_temperature']
        except KeyError:
            pass
        #: temperature change factor per iteration
        self.dtemp = None
        try:
            self.dtemp = self.parms['temperature_change_factor_per_iteration']
            if self.temp is None:
                log.warning(
                    'Because no initial temperature is given in the '
                    'configuration, the temperature is always zero; hence the '
                    'parameter `temperature_change_factor_per_iteration` does '
                    'not have any effect and should not be given either.')
                self.dtemp = None
        except KeyError:
            pass
        #: maximum number of iterations
        self.maxit = self.parms['max_number_of_iterations']
        #: number of rejections to converge
        self.max_rejected = self.maxit
        try:
            self.max_rejected = self.parms['max_number_of_rejections']
        except KeyError:
            pass
        #: maximum allowed distance between molecules (divergence criterion)
        self.abort_at_dist = None
        try:
            self.abort_at_dist = self.parms['max_separation']
        except KeyError:
            pass
        return True


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def parameters(self):
        """Configuration options for the Monte-Carlo conformational search:

            - "max_init_step":
                initial particle position range; for each transformation, this
                value is multiplied by its scaling and the initial
                transformation states are isotropically distributed within that
                range `(dtype=float, required=True)`

            - "initial_temperature":
                initial temperature `(dtype=float, required=False)`

            - "temperature_change_factor_per_iteration":
                temperature change factor per iteration `(dtype=float,
                required=False)`

            - "max_number_of_rejections":
                convergence criterion: number of iteration steps per degree of
                freedom without improvement of the score `(dtype=int,
                required=False)`

            - "max_number_of_iterations":
                number of iterations before the search is stopped if no
                convergence criterion has been reached before
                `(dtype=int, required=True)`

            - "max_separation":
                divergence criterion: maximum allowed distance between
                molecules `(dtype=float, default=1000.0)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='max_init_step', dtype=float_ge_zero,
            description='range of initial (randomized) positions / states',
            required=True))
        opt.append(Option(
            name='initial_temperature', dtype=float_ge_zero,
            description='initial temperature', required=False))
        opt.append(Option(
            name='temperature_change_factor_per_iteration',
            dtype=float_ge_zero, description='temperature change factor per '
            'iteration', required=False))
        opt.append(Option(
            name='max_number_of_rejections', dtype=int_gt_zero,
            description='convergence criterion: number of iteration steps '
            'without improvement of the score', required=False))
        opt.append(Option(
            name='max_number_of_iterations', dtype=int_ge_zero,
            description='maximum number of search iterations'))
        opt.append(Option(
            name='max_separation', dtype=float_gt_zero,
            description='divergence criterion: maximum allowed distance '
            'between molecules in Angstroem', default=1000.0))
        return opt
