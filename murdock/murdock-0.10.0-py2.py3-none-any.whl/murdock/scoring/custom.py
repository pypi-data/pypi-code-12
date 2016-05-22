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

"""
A scoring module using all terms from the :mod:`~murdock.scoring.pool`.

All terms declared in the scoring :class:`~murdock.scoring.pool` can be added.
Example setup in a configuration file to set up a custom scoring function with
the terms :class:`~murdock.scoring.pool.InterCollision`,
:class:`~murdock.scoring.pool.Coulomb` and
:class:`~murdock.scoring.pool.Shape4`:

.. code-block:: java

   "scoring": {
     "module": "scoring.custom",
     "parameters": {
       "terms": [
         {
           "class": "InterCollision",
           "parameters": {
             "weight": 100.0,
             "softness": 0.5
           }
         },
         {
           "class": "Coulomb",
           "parameters": {"weight": 0.5}
         },
         {
           "class": "Shape4",
           "parameters": {"weight": 0.5}
         }
       ]
         }
   }

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import murdock.config
import murdock.scoring
import murdock.scoring.pool


log = logging.getLogger('scoring.custom')


class Scoring(murdock.scoring.Scoring):

    def setup(self, parms, docking=None, name='custom', copy=False):
        #: scoring parameters, including a dictionary of scoring terms from
        #: the pool and their corresponding parameters
        self.parms = parms
        #: name of this scoring method
        self.name = name
        #: :class:`~murdock.runner.docking.Docking` instance using this
        #: :class:`Scoring` instance
        self.docking = docking
        # Add terms.
        for termconf in self.parms['terms']:
            termclass = termconf['class']
            termparms = termconf['parameters']
            term = murdock.scoring.pool.__dict__[termclass]()
            try:
                termname = termparms['name']
            except KeyError:
                termname = termclass
            try:
                termparms['offset'] = -self.parms['unbound_scores'][termname]
            except KeyError:
                pass
            self.add_term(term)
            if not term.setup(self.root, termparms):
                log.info('Error in setup of scoring term `%s`.', termname)
                return False
        # Initialize.
        self.init_interactions()
        return True


class ConfigDeclaration(murdock.scoring.pool.ConfigDeclaration):

    def parameters(self):
        """Configuration options for this custom scoring module:

            - "terms":
                dictionary of term names from the scoring term
                :class:`~murdock.scoring.pool.ConfigDeclaration` to
                be included in the scoring and their corresponding parameters
                `(dtype=dict, required=True)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='terms', dtype=list, description='scoring terms from the '
            'pool to be included in the scoring function and their parameters',
            required=True))
        return opt

    def terms(self):
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        poolterms = [
            u'%s' % _name for _name, _cls in
            murdock.scoring.pool.__dict__.items() if isinstance(_cls, type)]
        opt.append(Option(
            name='class', dtype=basestring, description='name of the scoring '
            'class from the pool', required=True, choices=poolterms))
        opt.append(Option(
            name='parameters', dtype=list, required=True, validate=False))
        return opt
