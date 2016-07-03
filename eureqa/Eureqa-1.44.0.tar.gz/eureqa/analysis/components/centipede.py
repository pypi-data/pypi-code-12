# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class Centipede(_Component):

    _component_type_str = 'CENTIPEDE_CARD'

    def __init__(self, datasource=None, search=None,
                 solution=None, use_all_data=None,
                 analysis=None, component_id=None, component_type=None):
        if datasource is not None:
            self.datasource = datasource

        if search is not None:
            self.search = search

        if solution is not None:
            self.solution = solution

        if use_all_data is not None:
            self.use_all_data = use_all_data

        super(Centipede, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :rtype: eureqa.DataSource
        """
        return getattr(self, "_datasource", None)

    @datasource.setter
    def datasource(self, val):
        self._datasource = val
        self._datasource_id = val._data_source_id
        self._update()

    @property
    def search(self):
        """The Search that is solved by this Explainer's Solution

        :rtype: eureqa.Search
        """
        return getattr(self, "_search", None)

    @search.setter
    def search(self, val):
        self._search_id = val._id
        self._search = val
        self._update()

    @property
    def solution(self):
        """The Solution that is being explained

        :rtype: eureqa.Solution
        """
        return getattr(self, "_solution", None)

    @solution.setter
    def solution(self, val):
        self._solution_id = val._id
        self._solution = val
        self._update()

    @property
    def use_all_data(self):
        """Use all data or just validation data?

        :rtype: bool
        """
        return getattr(self, "_use_all_data", None)

    @use_all_data.setter
    def use_all_data(self, val):
        self._use_all_data = val
        self._update()

    def _fields(self):
        return super(Centipede, self)._fields() + [ 'datasource_id', 'search_id', 'solution_id', 'use_all_data' ]

