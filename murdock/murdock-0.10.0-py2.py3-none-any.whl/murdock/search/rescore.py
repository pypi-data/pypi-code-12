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


"""Pseudo-search module which does not change the system but only rescores it.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import murdock.search


log = logging.getLogger('search.rescore')


class Search(murdock.search.Search):
    """Do not perform any search, only rescore and return.
    """

    def search(self):
        """Rescore and return.
        """
        self.scoring.rescore()
        if self.store_decoy_scores:
            self.add_score_to_history(
                self.scoring, label='decoys', total=False,
                weighted=False, unweighted=True)
        return True

    def setup(self):
        """Setup search settings and parameters.
        """
        self.name = 'rescore'
        return True


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def parameters(self):
        """Configuration options for the `rescore` pseudo-search:

        No options required.

        """
        opt = self.get_default_options()
        return opt
