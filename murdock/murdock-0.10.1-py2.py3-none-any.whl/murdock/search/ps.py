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
from builtins import range

import logging
import random

import scipy.constants

import murdock.transforms
import murdock.search


log = logging.getLogger('search.ps')


class SearchPSError(Exception):
    pass


class Search(murdock.search.Search):
    """Particle Swarm (PS) search.
    """

    def overwrite_input(self, part):
        """Overwrite input structure with best :class:`Particle` `part`.
        """
        part.root.update_source()
        diff = self.scoring.rescore()
        if round(part.best_score - self.scoring.total(), 5) != 0:
            raise SearchPSError(
                'The `best state` (scoring.total = %.6f) was just overwritten '
                'with a particle (best_score = %.6f, scoring.total = %.6f) '
                'but does not have the same score! This points to a crucial '
                'error in the search or scoring code used.' %
                (self.scoring.total(), part.best_score, part.scoring.total()))
        if round(diff, 5) > 0:
            after = self.scoring.total()
            before = after - diff
            raise SearchPSError(
                'The `best state` (score = %.6f) was just overwritten with a '
                'worse-scored state (score = %.6f). This points to a crucial '
                'error in the search or scoring code used.' % (before, after))
        return True

    def search(self):
        """Run Particle Swarm search.
        """
        # Initialize search
        log.info('Initialize swarm.')
        self.swarm = Swarm(search=self)
        log.info('Swarm with %d particles created.', len(self.swarm.parts))
        score_initial = self.swarm.best_part.best_score
        if self.intvideo is not None:
            self.intvideo.add_static(self.root)
            self.intvideo.init_cgos()
        # Run search
        self.iteration = 0
        for it in range(self.maxit):
            if self.iteration % max(1, int(self.maxit / 100)) == 0:
                self.log_status(
                    log.info, score_initial, message='rejected: %d / %d' %
                    (self.swarm.nrejects, self.nrejects))
                self.add_score_to_history(self.scoring)
                if (self.abort_at_dist is not None and
                        self.check_distance(self.root, self.abort_at_dist)):
                    return False
            if self.debugsampling:
                for part in self.swarm.parts:
                    for tf in part.transforms:
                        tf.source.history.append(tf.get_fmt_state())
            self.iteration += 1
            self.swarm.update()
            if self.iteration % self.video_interval == 0:
                if self.extvideo is not None:
                    self.extvideo.add_frame(self.root)
            if self.nrejects <= self.swarm.nrejects:
                log.info(
                    'System converged. No improvement within the last %d '
                    'iteration steps.', self.swarm.nrejects)
                return True
            if (self.iteration % self.ann_interval == 0
                    and self.min_nparts < len(self.swarm.parts)):
                worst_part = None
                worst_score = None
                for part in self.swarm.parts:
                    if worst_score is None or part.best_score > worst_score:
                        worst_part = part
                        worst_score = part.best_score
                self.swarm.parts.remove(part)
                log.info(
                    'Particle removed from swarm. %d particles left.',
                    len(self.swarm.parts))
        log.info('Maximum number of iterations (%d) reached.', self.maxit)
        self.add_score_to_history(self.scoring)
        return True

    def setup(self):
        """Set search settings and parameters.
        """
        self.name = 'Particle Swarm'
        #: current number of particles
        self.nparts = self.parms['init_number_of_particles']
        #: maximum number of particles
        self.min_nparts = self.parms['min_number_of_particles']
        #: maximum initial step length (this value is scaled using
        #: :attr:`~murdock.transforms.Transformation.scaling`)
        self.init_step = self.parms['max_init_step']
        #: initial (transformation) speed (this value is scaled using
        #: :attr:`~murdock.transforms.Transformation.scaling`)
        self.init_speed = self.parms['init_speed']
        #: maximum (transformation) speed (this value is scaled using
        #: :attr:`~murdock.transforms.Transformation.scaling`)
        self.max_speed = self.parms['max_speed']
        #: particle inertia
        self.w = None
        #: linear gradient for :attr:`w` given as list [start, end]
        self.w_range = None
        #: force / torque towards best particle state
        self.p = None
        #: linear gradient for :attr:`p` given as list [start, end]
        self.p_range = None
        #: current force / torque towards best swarm state
        self.g = None
        #: linear gradient for :attr:`g` given as list [start, end]
        self.g_range = None
        for a, a_ran in (('w', 'w_range'), ('p', 'p_range'), ('g', 'g_range')):
            if a in self.parms and a_ran in self.parms:
                log.fatal(
                    'Search parameters `%s` and `%s` are exclusive.', a, a_ran)
                return False
            elif a in self.parms:
                setattr(self, a, self.parms[a])
            elif a_ran in self.parms:
                setattr(self, a_ran, self.parms[a_ran])
        #: video frame interval
        self.video_interval = 1
        try:
            self.video_interval = self.parms['videoframe_interval']
        except KeyError:
            pass
        #: maximum number of iterations (convergence criterion)
        self.maxit = self.parms['max_number_of_iterations']
        #: number of rejections (convergence criterion)
        self.nrejects = self.maxit
        try:
            self.nrejects = self.parms['max_number_of_rejections']
        except KeyError:
            pass
        #: particle annihilation interval
        self.ann_interval = self.maxit
        try:
            self.ann_interval = self.parms['particle_annihilation_interval']
        except KeyError:
            pass
        #: score after each subtransformation individually
        self.score_substeps = self.parms['score_substeps']
        #: maximum allowed distance between molecules (divergence criterion)
        self.abort_at_dist = None
        try:
            self.abort_at_dist = self.parms['max_separation']
        except KeyError:
            pass
        # Automatically set transformation parameters, if not given.
        for tf in self.root.descendant_transforms():
            if tf.max_step is None:
                tf.max_step = self.max_speed * tf.scaling
            else:
                tf.max_step = min(tf.max_step, self.max_speed * tf.scaling)
        return True


class Particle(object):
    """A Particle Swarm Optimization agent.
    """

    def __init__(self, swarm, root, scoring):
        #: swarm containing this particle
        self.swarm = swarm
        #: root :class:`~murdock.tree.Node` defining this particle
        self.root = root
        #: :class:`~murdock.scoring.Scoring` instance used by this
        #: particle
        self.scoring = scoring
        #: `state()` of all transformations for best solution found by particle
        self.best_state = {}
        #: :class:`~murdock.transforms.Transformation` instances for this
        #: particle
        self.transforms = None
        self._init_transforms()

    def update(self):
        """Take a step (update states, velocities, scores and videos).
        """
        self._step()
        self._update_video()
        return True

    def update_best(self):
        """Save current particle state in :attr:`best_state`.
        """
        for tf in self.transforms:
            self.best_state[tf.source] = tf.state()
        self.best_score = self.scoring.total()
        self.swarm.update_best_part(self)
        return True

    def _init_transforms(self):
        """Collect particle transformations; initialize states and velocities.
        """
        self.transforms = [_tf for _tf in self.root.descendant_transforms()]
        for tf in self.transforms:
            tf.randomize_state(tf.scaling * self.swarm.search.init_step)
        for tf in self.transforms:
            tf.randomize_velocity(
                tf.scaling * self.swarm.search.init_speed, random_speed=False)
        self.scoring.rescore()
        return True

    def _step(self):
        """Update the particle transformation velocities and states.

        The change in velocity has three components:

            1) particle inertia: current velocity weighted by
               :attr:`~Search.w`
            2) particle attraction: a force / torque towards the best state
               found by this particle (:attr:`best_state`)
            3) swarm attraction: a force / torque towards the best state found
               by the swarm (:attr:`best_state` of :attr:`~Swarm.best_part`)

        """
        search = self.swarm.search
        tfs = list(self.transforms)
        random.shuffle(tfs)
        rp = random.random()
        rg = random.random()
        for tf in self.transforms:
            tf.update_velocity(
                search.w, (rp * search.p, self.best_state[tf.source]),
                (rg * search.g, self.swarm.best_part.best_state[tf.source]))
            tf.step()
            if search.score_substeps:
                self._update_score(tf.node)
        if not search.score_substeps:
            self._update_score()
        return True

    def _update_video(self):
        search = self.swarm.search
        if (search.intvideo is not None and
                search.iteration % search.video_interval == 0):
            search.intvideo.add_frame(self.root)
            if self is self.swarm.best_part:
                color = (1.0, 0.0, 0.0)
                radius = 2.5
            else:
                color = (0.0, 0.0, 1.0)
                radius = 1.0
            i_obj = 0
            for tf, p in self.best_state.items():
                if not isinstance(tf, murdock.transforms.Translation):
                    continue
                i_obj += 1
                cgo_name = '%s_center_%d' % (self.root.name, i_obj)
                search.intvideo.add_sphere(
                    name=cgo_name, coords=p, radius=radius, color=color)
        return True

    def _update_score(self, node=None):
        """Update the particle score.
        """
        ds = self.scoring.rescore(node)
        s = self.scoring.total()
        if s < self.best_score:
            self.update_best()
        return s, ds


class Swarm(object):
    """A swarm of birds, fish or molecular systems.
    """

    def __init__(self, search):
        #: search algorithm using this swarm
        self.search = search
        #: particle with best :attr:`Particle.best_score`
        self.best_part = None
        #: particles in swarm
        self.parts = []
        # Create particles
        for i in range(search.nparts):
            r_copy = search.root.deepcopy(suffix='_particle%04d' % (
                len(self.parts) + 1))
            s_copy = search.scoring.deepcopy(root=r_copy)
            part = Particle(swarm=self, root=r_copy, scoring=s_copy)
            self.parts.append(part)
        #: number of updates without change of :attr:`best_part`
        self.nrejects = 0
        for part in self.parts:
            part.update_best()

    def update(self):
        """Iterate swarm one step (update all velocities, states and scores).
        """
        for a, a_ran in (('w', 'w_range'), ('p', 'p_range'), ('g', 'g_range')):
            try:
                v1, v2 = getattr(self.search, a_ran)
            except TypeError:
                continue
            setattr(
                self.search, a, v1 +
                self.search.iteration * float(v2 - v1) / self.search.maxit)
        self.nrejects += 1
        parts = list(self.parts)
        random.shuffle(parts)
        for part in parts:
            part.update()
            if self.search.store_decoy_scores:
                self.search.add_score_to_history(
                    part.scoring, label='decoys', total=False,
                    weighted=False, unweighted=True)
        return True

    def update_best_part(self, part=None):
        """Store the best particle in :attr:`best_part`.
        """
        if (
                self.best_part is None or part.best_score <
                self.best_part.best_score):
            self.best_part = part
            if part.best_score < self.search.scoring.total():
                self.search.overwrite_input(part)
            self.nrejects = 0
        return True


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def parameters(self):
        """Configuration options for the Particle Swarm search:

            - "init_number_of_particles":
                initial number of particles `(dtype=int, required=True)`

            - "max_init_step":
                initial particle position range; for each transformation, this
                value is multiplied by its scaling and the initial
                transformation states are isotropically distributed within that
                range `(dtype=float, default=1.0)`

            - "init_speed":
                initial particle speed; for each transformation, this value is
                multiplied by its scaling `(dtype=float, required=True)`

            - "max_speed":
                maximum particle speed (stabilizes trajectories); for each
                transformation, this value is multiplied by its scaling
                `(dtype=float, default=2/3)`

            - "w":
                fraction of velocity conserved between iterations (determines
                exploration capacity)
                `(dtype=float, required if `w_range` is not set)`

            - "w_range":
                fraction of velocity conserved between iterations (determines
                exploration capacity); linear gradient given as [start, end]
                `(dtype=list, required if `w` is not set)`

            - "p":
                attraction to best particle solution (determines local search
                capacity) `(dtype=float, required if `p_range` is not set)`

            - "p_range":
                attraction to best particle solution (determines local search
                capacity); linear gradient given as [start, end]
                `(dtype=float, required if `p` is not set)`

            - "g":
                attraction to best swarm solution (determines global search
                capacity) `(dtype=float, required if `g_range` is not set)`

            - "g_range":
                attraction to best swarm solution (determines global search
                capacity); linear gradient given as [start, end]
                `(dtype=float, required if `g` is not set)`

            - "videoframe_interval":
               number of iterations between two video frames
               `(dtype=int, required=False)`

            - "min_number_of_particles":
                number of particles at which annihilation is stopped
                `(dtype=int, required=False)`

            - "particle_annihilation_interval":
                number of iteration steps between two particle annihilations
                `(dtype=int, required=False)`

            - "score_substeps":
                score after each transformation individually (increases
                sampling while significantly increasing computational time)
                `(dtype=bool, default=False)`

            - "max_number_of_rejections":
                convergence criterion: number of iteration steps without
                improvement of the best swarm state
                `(dtype=int, required=False)`

            - "max_number_of_iterations":
                number of iterations before the search is stopped if no
                convergence criterion has been reached before
                `(dtype=int, required=True)`

            - "max_separation":
                divergence criterion: maximum allowed distance between
                molecules in Angstroem `(dtype=float, default=1000.0)`

        """
        Option = murdock.config.ConfigOption
        def list_of_two_floats(l):
            a, b = [Option.float_ge_zero(_x) for _x in l]
            return a, b
        opt = self.get_default_options()
        opt.append(Option(
            name='max_number_of_iterations', dtype=Option.int_ge_zero,
            description='maximum number of search iterations'))
        opt.append(Option(
            name='init_number_of_particles', dtype=Option.int_gt_zero,
            description='initial number of particles'))
        opt.append(Option(
            name='max_init_step', dtype=Option.float_ge_zero,
            description='range of initial (randomized) particle states',
            default=1.0))
        opt.append(Option(
            name='init_speed', dtype=Option.float_ge_zero,
            description='initial particle speed'))
        opt.append(Option(
            name='max_speed', dtype=Option.float_ge_zero,
            description='maximum particle speed', default=2./3))
        opt.append(Option(
            name='w', dtype=Option.float_ge_zero, required=False,
            description='fraction of velocity conserved between iterations'))
        opt.append(Option(
            name='w_range', dtype=list_of_two_floats, required=False,
            description='fraction of velocity conserved between iterations; '
            'linear gradient given as [start, end]'))
        opt.append(Option(
            name='p', dtype=Option.float_ge_zero, required=False,
            description='attraction to the best particle solution'))
        opt.append(Option(
            name='p_range', dtype=list_of_two_floats, required=False,
            description='attraction to the best particle solution; '
            'linear gradient given as [start, end]'))
        opt.append(Option(
            name='g', dtype=Option.float_ge_zero, required=False,
            description='attraction to the best swarm solution'))
        opt.append(Option(
            name='g_range', dtype=list_of_two_floats, required=False,
            description='attraction to the best swarm solution; '
            'linear gradient given as [start, end]'))
        opt.append(Option(
            name='videoframe_interval', dtype=Option.int_ge_zero,
            description='number of iterations between two video frames',
            required=False))
        opt.append(Option(
            name='score_substeps', dtype=bool,
            description='score after each transformation individually ',
            default=False))
        opt.append(Option(
            name='max_number_of_rejections', dtype=Option.int_gt_zero,
            description='convergence criterion: number of iteration steps '
            'without improvement of the best swarm state', required=False))
        opt.append(Option(
            name='min_number_of_particles', dtype=Option.int_ge_zero,
            description='number of particles at which annihilation is stopped',
            default=0))
        opt.append(Option(
            name='particle_annihilation_interval', dtype=Option.int_gt_zero,
            description='number of iterations between two particle '
            'annihilations', required=False))
        opt.append(Option(
            name='max_separation', dtype=Option.float_gt_zero,
            description='divergence criterion: maximum allowed distance '
            'between molecules in Angstroem', default=1000.0))
        return opt
