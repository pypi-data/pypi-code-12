# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015-2016 Tiago Baptista
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

"""
This module provides several ready-made visual classes. Used mainly for the
examples given in the Complex Systems course. In this current version, these
should not be considered stable in terms of API.

"""

from __future__ import division
from . import MplVisual, Simulator, Visual
from .simulators import FunctionIterator, FunctionIterator2D, FinalStateIterator
import numpy as np
from matplotlib.transforms import Affine2D
import pyglet

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'


class Line(MplVisual):
    def __init__(self, sim: Simulator, x: list, y: list, auto_size=True,
                 **kwargs):
        super(Line, self).__init__(sim, **kwargs)

        self._auto_size = auto_size

        self._x = x
        self._y = y

        self.ax = self.figure.add_subplot(111)
        self.l, = self.ax.plot(self._x, self._y)

    def draw(self):
        self.l.set_data(self._x, self._y)
        if self._auto_size:
            self.ax.relim()
            self.ax.autoscale_view()


class Lines(MplVisual):
    def __init__(self, sim: Simulator, auto_size=True, **kwargs):
        super(Lines, self).__init__(sim, **kwargs)

        self._auto_size = auto_size

        self.ax = self.figure.add_subplot(111)
        self._lines = []
        for i in range(len(self.sim.y)):
            line, = self.ax.plot(self.sim.x, self.sim.y[i])
            self._lines.append(line)

    def draw(self):
        for i in range(len(self._lines)):
            self._lines[i].set_data(self.sim.x, self.sim.y[i])

        if self._auto_size:
            self.ax.relim()
            self.ax.autoscale_view()


class TimeSeries(Lines):
    def __init__(self, sim: FunctionIterator, **kwargs):
        super(TimeSeries, self).__init__(sim, **kwargs)

        self.ax.set_title('Time Series')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('State')


class PhaseSpace2D(Line):
    def __init__(self, sim: FunctionIterator2D, name_x, name_y, **kwargs):
        super(PhaseSpace2D, self).__init__(sim, sim.y[0], sim.y[1], **kwargs)

        self.ax.set_title('Phase Space')
        self.ax.set_xlabel(name_x)
        self.ax.set_ylabel(name_y)


class CobWebVisual(MplVisual):
    def __init__(self, sim: FunctionIterator, min_x, max_x, func_string='',
                 **kwargs):
        super(CobWebVisual, self).__init__(sim, **kwargs)

        self.ax = self.figure.add_subplot(111)

        # PLot function
        x = np.linspace(min_x, max_x, 1000)
        func_vec = np.frompyfunc(self.sim.func)
        y = func_vec(x)
        self.ax.plot(x, y, label='$f(x)=$' + func_string)

        # Plot f(x) = x
        self.ax.plot(x, x, ':k', label='$f(x)=x$')

        # Create initial cobweb plots
        self._cobx = [[x[0]] for x in self.sim.y]
        self._coby = [[0] for x in self.sim.y]
        self._cobweb_lines = []
        for i in range(len(self.sim.y)):
            line, = self.ax.plot(self._cobx[i], self._coby[i],
                                 label='$x_0=' + str(self.sim.y[i][0]) + '$')
            self._cobweb_lines.append(line)

    def draw(self):
        for i in range(len(self._cobweb_lines)):
            self._cobx[i].append(self.sim.y[i][-2])
            self._coby[i].append(self.sim.y[i][-2])
            self._cobx[i].append(self.sim.y[i][-2])
            self._coby[i].append(self.sim.y[i][-1])

            self._cobweb_lines[i].set_data(self._cobx[i], self._coby[i])


class FinalStateDiagram(MplVisual):
    def __init__(self, sim: FunctionIterator, discard_initial=1000, **kwargs):
        super(FinalStateDiagram, self).__init__(sim, **kwargs)

        self._discard_initial = discard_initial
        self._seeds = [y[0] for y in self.sim.y]

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Final State Diagram')
        x_min = min([y[0] for y in self.sim.y])
        x_max = max([y[0] for y in self.sim.y])
        self.ax.set_xlim(x_min - 0.5, x_max + 0.5)
        self.ax.set_xlabel('$t={}$'.format(self.sim.time))
        self.ax.set_ylabel('Final Value(s)')

    def draw(self):
        self.ax.set_xlabel('$t={}$'.format(self.sim.time))
        if self.sim.time >= self._discard_initial:
            for i in range(len(self.sim.y)):
                self.ax.scatter([self._seeds[i]], self.sim.y[i][-1:], c='black')


class BifurcationDiagram(MplVisual):
    def __init__(self, sim: FinalStateIterator, **kwargs):
        super(BifurcationDiagram, self).__init__(sim, **kwargs)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Bifurcation Diagram')
        self.ax.set_xlabel('a')
        self.ax.set_ylabel('Final Value(s)')
        self.ax.set_xlim(sim.start, sim.end)
        self.ax.set_ylim(0, 1)
        self.ax.grid()

    def draw(self):
        self.ax.scatter(self.sim.x, self.sim.y, s=0.5, c='black')


class Points2D(Visual):
    def __init__(self, sim, screen_transform=None, **kwargs):
        super(Points2D, self).__init__(sim, **kwargs)

        if screen_transform is not None:
            self._screen_transform = screen_transform
        else:
            self._screen_transform = Affine2D().scale(self.width, self.height)
        self._batch = pyglet.graphics.Batch()

    def draw(self):
        if self.sim.draw_points:
            points = self.sim.draw_points

            for i in range(len(points)):
                p = self._screen_transform.transform_point(points[i])
                self._batch.add(1, pyglet.gl.GL_POINTS, None, ('v2f', p),
                               ('c3B', (255, 255, 255)))

            self.sim.draw_points.clear()

        self._batch.draw()
