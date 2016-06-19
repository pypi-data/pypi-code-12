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
import warnings

class EvaluateModel(_Component):

    _component_type_str = 'EVALUATE_MODEL'

    def __init__(self, evaluationInfo=None,
                 originalSolutionInfo=None, datasource=None, search=None, solution=None,
                 analysis=None, component_id=None, component_type=None):
        if evaluationInfo is not None:
            self._evaluationInfo = evaluationInfo
        else:
            self._evaluationInfo = []  # Backend requires the empty list at minimum

        if originalSolutionInfo is not None:
            self._originalSolutionInfo = originalSolutionInfo

        if datasource is not None:
            self.datasource = datasource

        if search is not None:
            self.search = search

        if solution is not None:
            self.solution = solution

        super(EvaluateModel, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)


    class SolutionInfo(object):
        """ The solution information for a single model evaluation ("tab")
        on ModelEvaluatorCard

        :param eureqa.data_source.DataSource datasource: Data source for this solution
        :param eureqa.solution.Solution solution: Solution

        :var str ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.datasource_id: ID of the DataSource referenced by this solution-tab
        :var str ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.search_id: ID of the Search referenced by this solution-tab
        :var str ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.solution_id: ID of the Solution referenced by this solution-tab
        :var bool ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.has_target_variable: Whether the datasource contains the target variable
        """

        def __init__(self, component, body, datasource=None, search=None, solution=None):
            """ SolutionInfo init """
            if hasattr(component, "_analysis"):
                self._eureqa = component._analysis._eureqa
            self._component = component
            self._from_json(body, datasource, search, solution)

        @classmethod
        def _from_datasource_and_solution(cls, component, datasource, solution):
            return cls(
                component=component,
                body={
                    "datasource_id": datasource._data_source_id,
                    "search_id": solution.search._id,
                    "solution_id": solution._id
                },
                datasource=datasource,
                solution=solution,
                search=solution.search)

        def _to_json(self):
            return self._body

        def _from_json(self, body, datasource=None, search=None, solution=None):
            self._body = body

            datasource_id = body.get("datasource_id")
            search_id = body.get("search_id")
            solution_id = body.get("solution_id")

            if datasource_id and (not datasource or datasource._data_source_id != datasource_id):
                datasource = self._eureqa.get_data_source_by_id(datasource_id)
            if datasource_id and search_id and (not search or search._id != search_id):
                search = self._eureqa._get_search_by_search_id(datasource_id, search_id)
            if datasource_id and search_id and solution_id and (not solution or solution._id != solution_id):
                solution = self._eureqa._get_solution_by_id(datasource_id, search_id, solution_id)

            self._datasource = datasource
            self._search = search
            self._solution = solution

            if datasource and solution:
                target_variable = datasource.get_variable_details(solution.target)
                body['hasTargetVariable'] = target_variable is not None and target_variable.distinct_values > 0

        @property
        def datasource(self):
            """The data source providing data for this component

            :rtype: eureqa.DataSource
            """
            return getattr(self, "_datasource", None)

        @datasource.setter
        def datasource(self, val):
            self._datasource = val
            self._body["datasource_id"] = val._data_source_id
            self._update()

        @property
        def datasource_id(self):
            warnings.warn("'SolutionInfo.datasource_id' is deprecated; use 'SolutionInfo.datasource' instead",
                          DeprecationWarning)
            return self.datasource._data_source_id

        @datasource_id.setter
        def datasource_id(self, val):
            warnings.warn("'SolutionInfo.datasource_id' is deprecated; use 'SolutionInfo.datasource' instead",
                          DeprecationWarning)
            self._body["datasource_id"] = val
            self.datasource = self._eureqa.get_data_source_by_id(val)

        @property
        def search(self):
            """The Search that is solved by this Explainer's Solution

            :rtype: eureqa.Search
            """
            return getattr(self, "_search", None)

        @search.setter
        def search(self, val):
            self._search_id = val._id
            self._body["search"] = val
            self._update()

        @property
        def search_id(self):
            warnings.warn("'SolutionInfo.search_id' is deprecated; use 'SolutionInfo.search_id' instead",
                          DeprecationWarning)
            return self.search._id

        @search_id.setter
        def search_id(self, val):
            warnings.warn("'SolutionInfo.search_id' is deprecated; use 'SolutionInfo.search_id' instead",
                          DeprecationWarning)
            self._body["search_id"] = val
            self.search = self._eureqa._get_search_by_search_id(self._body["datasource_id"], val)

        @property
        def solution(self):
            """The Solution that is being explained

            :rtype: eureqa.Solution
            """
            return getattr(self, "_solution", None)

        @solution.setter
        def solution(self, val):
            self._solution_id = val._id
            self._body["solution"] = val
            self._update()

        @property
        def solution_id(self):
            warnings.warn("'SolutionInfo.solution_id' is deprecated; use 'SolutionInfo.search_id' instead",
                          DeprecationWarning)
            return self.solution._id

        @solution_id.setter
        def solution_id(self, val):
            warnings.warn("'SolutionInfo.solution_id' is deprecated; use 'SolutionInfo.search_id' instead",
                          DeprecationWarning)
            self._body["solution_id"] = val
            self.solution = self._eureqa._get_solution_by_id(self._body["datasource_id"], self._body["search_id"], val)

        @property
        def has_target_variable(self):
            """Whether the datasource contains the target variable

            :return: Whether the datasource contains the target variable
            """
            return self._body.get('hasTargetVariable')

        @has_target_variable.setter
        def has_target_variable(self, val):
            self._body['hasTargetVariable'] = val
            self._update()

        @property
        def accuracy(self):
            """
            Accuracy of this Solution.  Rendered as a human-readable pretty-printed string.

            :rtype: str
            """
            return self._body.get("accuracy")

        @accuracy.setter
        def accuracy(self, val):
            self._body["accuracy"] = val
            self._update()

        @property
        def is_fetching(self):
            return self._body.get("isFetching")

        @is_fetching.setter
        def is_fetching(self, val):
            self._body["isFetching"] = val
            self._update()

        def _update(self):
            self._component._update()
            self._from_json(self._body, self._datasource, self._search, self._solution)

    def add_solution_info(self, datasource, solution):
        """Add a new (non-default) solution and tab to this card.
        Once added, this object will show up in the list returned by `solution_infos`.

        :param DataSource datasource: DataSource used with this solution.
        :param Solution solution: Solution associated with the model evaluation.
        """
        solution_info = self.SolutionInfo._from_datasource_and_solution(self, datasource, solution)

        if not hasattr(self, "_originalSolutionInfo"):
            # First submission gets added as the original solution info
            self._originalSolutionInfo = solution_info._to_json()
            return

        self._evaluationInfo.append(solution_info._to_json())
        self._update()

    @property
    def solution_infos(self):
        """The set of all SolutionInfo objects associated with this card.
        One per solution tab displayed in the UI.
        Note that `solution_infos[0]` is the default card; it may be treated specially by the UI.

        To add a solution, use the "add_solution_info()" method.

        :return: List or tuple of SolutionInfo objects
        """
        # Pass in our datasource/search/solution in case they are the same as that of the new SolutionInfo.
        # Saves an RPC round-trip for each if so.
        # SolutionInfo is responsible for figuring out that we passed in the wrong objects and silently ignoring them.
        return tuple(self.SolutionInfo(self, x, self.datasource, self.search, self.solution) for x in
                     (([self._originalSolutionInfo] if hasattr(self, "_originalSolutionInfo") else []) +
                      getattr(self, "_evaluationInfo", [])))
    # No setter.  Mutate the returned SolutionInfo objects or use the "add_solution_info" method.


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


    def _fields(self):
        return super(EvaluateModel, self)._fields() + [ 'evaluationInfo', 'originalSolutionInfo', 'datasource_id', 'search_id', 'solution_id' ]

