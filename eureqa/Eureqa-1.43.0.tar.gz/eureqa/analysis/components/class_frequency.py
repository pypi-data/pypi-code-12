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

class ClassFrequency(_Component):

    _component_type_str = 'CLASS_FREQUENCY'

    def __init__(self, evaluationInfo=None, originalSolutionInfo=None, datasource_id=None, search_id=None,
                 solution_id=None, analysis=None, component_id=None, component_type=None):
        if evaluationInfo is not None:
            self._evaluationInfo = evaluationInfo

        if originalSolutionInfo is not None:
            self._originalSolutionInfo = originalSolutionInfo

        if datasource_id is not None:
            self._datasource_id = datasource_id

        if search_id is not None:
            self._search_id = search_id

        if solution_id is not None:
            self._solution_id = solution_id

        super(ClassFrequency, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)


    @property
    def evaluationInfo(self):
        return self._evaluationInfo

    @evaluationInfo.setter
    def evaluationInfo(self, val):
        self._evaluationInfo = val
        self._update()

        
    @property
    def originalSolutionInfo(self):
        return self._originalSolutionInfo

    @originalSolutionInfo.setter
    def originalSolutionInfo(self, val):
        self._originalSolutionInfo = val
        self._update()

        
    @property
    def datasource_id(self):
        return self._datasource_id

    @datasource_id.setter
    def datasource_id(self, val):
        self._datasource_id = val
        self._update()

        
    @property
    def search_id(self):
        return self._search_id

    @search_id.setter
    def search_id(self, val):
        self._search_id = val
        self._update()

        
    @property
    def solution_id(self):
        return self._solution_id

    @solution_id.setter
    def solution_id(self, val):
        self._solution_id = val
        self._update()

        

    def _fields(self):
        return super(ClassFrequency, self)._fields() + [ 'evaluationInfo', 'originalSolutionInfo', 'datasource_id', 'search_id', 'solution_id' ]

