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

class ModelFitPlotCard(AnalysisCard):
    """Represents a projection card on the server.  Common base class for all projection cards.

    :param ~eureqa.Solution solution: The Solution object for which this card is being created
    :param str x_axis: The card's X axis label
    :param str title: The card's title.
    :param str description: The card's description.
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.model_fit_plot_card.ModelFitPlotCard.title: The card's title.
    :var str ~eureqa.analysis_cards.model_fit_plot_card.ModelFitPlotCard.x_axis: The card's X axis
    """

    def __init__(self, solution=None, x_axis=None, title=None, description=None, collapse=False):
        """ ModelFitPlotCard init """

        super(ModelFitPlotCard, self).__init__()

        self.solution = solution
        self.x_axis = x_axis
        self.title = title
        self.description = description
        self.collapse = collapse

    @property
    def x_axis(self):
        """The x_axis option for this card.

        :return: x axis for this card
        :rtype: str
        """
        
        return self._options['x_axis']

    @x_axis.setter
    def x_axis(self, val):
        self._options['x_axis'] = val
        self._update_card()

    @property
    def title(self):
        """The title of this card.

        :return: title of this card
        :rtype: str
        """
        
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
    def options(self):
        """The configuration options for this card.

        :returns: Object representing configuration options
        """
        
        return self._Options(self)

    @options.setter
    def options(self, var):
        ## Allow either an _Options object or a dictionary.
        ## _Options object in case of assignment from another card;
        ## dict because _Options objects can't be created from scratch
        ## and can't exist standalone.
        if isinstance(var, _Options):
            self._body['content']['options'] = var._parent_card._body['content']['options']
        else:  ## assume a dictionary-like object
            self._body['content']['options'].clear()
            self._body['content']['options'].update(var)
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
