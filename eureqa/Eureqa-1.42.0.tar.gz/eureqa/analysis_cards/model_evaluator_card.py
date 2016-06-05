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

from analysis_card import AnalysisCard
import json

class ModelEvaluatorCard(AnalysisCard):
    """Represents an evaluate model card on the server.

    :param str title: Title of the card.  Defaults to 'Evaluate Model'.
    :param str description: Description of the card.
    :param bool collapse: Whether the card should default to be collapsed.
    :param list(eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo) solution_infos: List of solutions that this card is rendering

    :var str ~eureqa.analysis_cards.ModelEvaluatorCard.title: The title of the card
    :var tuple ~eureqa.analysis_cards.ModelEvaluatorCard.solution_infos: Immutable ordered set of SolutionInfo objects representing the solutions shown on this card.
    """
    _item_type = 'EVALUATE_MODEL'

    def __init__(self, title=None, description=None, collapse=False, solution_infos=None):
        """ ModelEvaluatorCard init """

        super(ModelEvaluatorCard, self).__init__()

        if not solution_infos:
            solution_infos = []

        self.title = title
        self.description = description
        self.collapse = collapse

        if 'content' not in self._body:
            self._body['content'] = {}

        if len(solution_infos) >= 1:
            self._body['content']['originalSolutionInfo'] = solution_infos[0].to_json()
        self._body['content']['evaluationInfo'] = [x.to_json() for x in solution_infos[1:]]

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

        def __init__(self, datasource=None, solution=None):
            """ SolutionInfo init """

            self._dict = {}
            if datasource:
                self.datasource_id = datasource._data_source_id
            if solution:
                self.search_id = solution.search._id
                self.solution_id = solution._id

            if datasource and solution:
                target_variable = datasource.get_variable_details(solution.target)
                has_target_variable = target_variable is not None and target_variable.distinct_values > 0
                self.has_target_variable = has_target_variable


        def to_json(self):
            return self._dict

        @classmethod
        def from_json(cls, card, backing_dict):
            assert isinstance(backing_dict, dict)

            obj = cls()
            obj._card = card
            obj._dict = backing_dict
            return obj

        def _update_card(self):
            if hasattr(self, '_card'):
                self._card._update_card()

        @property
        def datasource_id(self):
            """ID of the DataSource used for this solution

            :return: unique DataSource identifier
            """
            return self._dict['datasource_id']

        @datasource_id.setter
        def datasource_id(self, val):
            self._dict['datasource_id'] = val
            self._update_card()

        @property
        def search_id(self):
            """ID of the Search used for this solution

            :return: unique Search identifier
            """
            return self._dict['search_id']

        @search_id.setter
        def search_id(self, val):
            self._dict['search_id'] = val
            self._update_card()

        @property
        def solution_id(self):
            """ID of the Solution used for this solution

            :return: unique Solution identifier
            """
            return self._dict['solution_id']

        @solution_id.setter
        def solution_id(self, val):
            self._dict['solution_id'] = val
            self._update_card()
            
        @property
        def has_target_variable(self):
            """Whether the datasource contains the target variable

            :return: Whether the datasource contains the target variable
            """
            return self._dict['hasTargetVariable']

        @has_target_variable.setter
        def has_target_variable(self, val):
            self._dict['hasTargetVariable'] = val
            self._update_card()

    @property
    def title(self):
        """The title of this card.

        :return: title of this card
        :rtype: str"""
        return self._body['content']['title']

    @title.setter
    def title(self, value):
        self._body['content']['title'] = value
        self._update_card()

    @property
    def description(self):
        """ The description of this card.

        :return: description of this card
        :rtype: str"""
        return self._body['content']['description']

    @description.setter
    def description(self, value):
        self._body['content']['description'] = value
        self._update_card()
        
    @property
    def collapse(self):
        """Whether the card is collapsed by default.

        :return: whether the card is collapsed by default
        :rtype: str"""
        return self._body.get('collapse')

    @collapse.setter
    def collapse(self, value):
        self._body['collapse'] = value
        self._update_card()

    def add_solution_info(self, datasource, solution):
        """Add a new (non-default) solution and tab to this card.
        Once added, this object will show up in the list returned by `solution_infos`.

        :param DataSource datasource: DataSource used with this solution.
        :param Solution solution: Solution associated with the model evaluation.
        """
        has_target_variable = solution.target in datasource.get_variables()
        if not 'evaluationInfo' in self._body['content']:
            self._body['content']['evaluationInfo'] = []
        self._body['content']['evaluationInfo'].append(self.SolutionInfo(datasource, solution).to_json())
        self._update_card()
        
    @property
    def solution_infos(self):
        """The set of all SolutionInfo objects associated with this card.
        One per solution tab displayed in the UI.
        Note that `solution_infos[0]` is the default card; it may be treated specially by the UI.

        :return: List or tuple of SolutionInfo objects
        """
        return tuple(self.SolutionInfo.from_json(self, x) for x in
                     ([self._body['content']['originalSolutionInfo']] +
                      (self._body['content']['evaluationInfo'] if 'evaluationInfo' in self._body['content'] else [])))
    ## No setter.  Mutate the returned SolutionInfo objects or use the "add_solution_info" method.

    
