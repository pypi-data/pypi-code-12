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

from text_card import TextCard
from plot import Plot

class CustomPlotCard(TextCard):
    """Represents a card which can display a custom plot.

    :param eureqa.analysis_cards.Plot plot: The Plot to be displayed in the card.
    :param str title: The card title.
    :param str description: The card's description.
    :param bool collapse: Whether the card should default to be collapsed.

    :var eureqa.analysis_cards.Plot plot: the underlying Plot displayed by this card.
    """
    _item_type = 'CUSTOM_GRAPH'

    def __init__(self, plot=None, title=None, description=None, collapse=False):
        """ """

        super(CustomPlotCard, self).__init__()

        self.title = title
        self.description = description
        self.collapse = collapse
        self.plot = plot

    @property
    def _plot(self):
        return Plot._from_json(self._options, self._eureqa)

    @property
    def plot(self):
        """The underlying Plot displayed by this card."""
        return self._plot

    @plot.setter
    def plot(self, val):
        self._options = val._to_json() if val else None

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


    def delete(self):
        """Deletes the card from the server.

        This will delete any data which has been uploaded internally to support plotting.
        """
        self._plot.delete()
        TextCard.delete(self)
