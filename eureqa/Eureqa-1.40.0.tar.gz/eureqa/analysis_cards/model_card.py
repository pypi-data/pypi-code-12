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


class ModelCard(AnalysisCard):
    """Represents a model card on the server.

    :param eureqa.Solution solution: The solution that will be displayed on the card.
    :param str title: The card title.
    :param str description: The card description.
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.ModelCard.title: The card title.
    :var str ~eureqa.analysis_cards.ModelCard.description: The card description.
    """
    _item_type = "INTERACTIVE_EXPLAINER"

    def __init__(self, solution=None, title=None, description=None, collapse=False):
        """ ModelCard init """

        super(ModelCard, self).__init__()

        self.title = title
        self.description = description
        self.collapse = collapse
        self.solution = solution

    @property
    def title(self):
        """The title of this card.

        :return: title of this card
        :rtype: str"""
        return self._body['content']['title'] if 'title' in self._body['content'] else None

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
        return self._body['collapse']

    @collapse.setter
    def collapse(self, value):
        self._body['collapse'] = value
        self._update_card()

    @property
    def solution(self):
        """
        :return: Solution that the card is rendering
        :rtype: ~eureqa.solution.Solution
        """
        return self._eureqa._get_solution_by_id(self._body['dependencies'][0]['solution_id'])

    @solution.setter
    def solution(self, val):
        self._body['dependencies'] = [{
            'datasource_id': val.search._data_source_id,
            'search_id': val.search._id,
            'solution_id': val._id
        }] if val else None
        self._update_card()
