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

class DistributionPlotCard(AnalysisCard):
    """Represents a distribution plot card on the server.

    :param eureqa.DataSource datasource: The data source to which the variable belongs.
    :param str variable: The name of the variable that will be displayed on the card.
    :param str title: The card title.
    :param str description: The card's description.
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.DistributionPlotCard.title: The card title.
    :var str ~eureqa.analysis_cards.DistributionPlotCard.datasource: The datasource used by the card.
    :var str ~eureqa.analysis_cards.DistributionPlotCard.variable: The variable plotted by the coard.
    """
    _item_type = "VARIABLE_DISTRIBUTION_PLOT"

    def __init__(self, datasource=None, variable=None, title=None, description=None, collapse=False):
        """ DistributionPlotCard init """

        super(DistributionPlotCard, self).__init__()
        self.datasource = datasource
        self.variable = variable
        self.title = title
        self.description = description
        self.collapse = collapse

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
        return self._body['collapse']

    @collapse.setter
    def collapse(self, value):
        self._body['collapse'] = value
        self._update_card()

    @property
    def datasource(self):
        if len(self._body['dependencies']) == 0:
            return None
        return self._eureqa._get_data_source_by_id(self._body['dependencies'][0]['datasource_id'])

    @datasource.setter
    def datasource(self, val):
        if len(self._body['dependencies']) == 0:
            self._body['dependencies'] = [{'datasource_id': None, 'variable_name': None}]
        self._body['dependencies'][0]['datasource_id'] = val._data_source_id if val else None
        self._update_card()

    @property
    def variable(self):
        if len(self._body['dependencies']) == 0:
            return None
        return self._body['dependencies'][0]['variable_name']

    @variable.setter
    def variable(self, val):
        if len(self._body['dependencies']) == 0:
            self._body['dependencies'] = [{'datasource_id': None, 'variable_name': None}]
        self._body['dependencies'][0]['variable_name'] = val
        self._update_card()
