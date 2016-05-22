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

import json
import copy

from eureqa.utils.channel import _Channel

class AnalysisCard(object):
    """The base class for all card classes. API returns an instance of this class if it cannot recognize
    the type of the card that it receives from the server.

    Don't construct this class directly.  Instead, construct any class that inherits from it.

    :param object: A configuration object used internally
    """

    def __init__(self):
        """For internal use only"""
        self._body = {
            'content': {},
            'dependencies': [],
            'item_type': self._item_type
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, json.dumps(self._body))

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
    def _analysis_id(self):
        return self._body.get('analysis_id')
    ## No setter:  Value should not be modified

    @property
    def _id(self):
        return self._body.get('item_id')
    ## No setter:  Value should not be modified

    @property
    def _order(self):
        return self._body.get('order_index')

    @_order.setter
    def _order(self, val):
        self._body['order_index'] = val

    @property
    def _options(self):
        if 'content' not in self._body:
            self._body['content'] = {}
        if 'options' not in self._body['content']:
            self._body['content']['options'] = {}

        return self._body['content']['options']

    @_options.setter
    def _options(self, val):
        if 'content' not in self._body:
            self._body['content'] = {}
        self._body['content']['options'] = val

    def to_json(self):
        """ Convert this AnalysisCard to a JSON-serializable structure

        :return: A representation of this card's contents as primitive Python objects
        """
        return self._body

    @classmethod
    def from_json(cls, body, eureqa=None):
        """ Construct a new AnalysisCard from the output of 'to_json()'

        :param obj cls: Classmethod object
        :param dict body: Content of the card
        :param Eureqa eureqa: Eureqa-API instance
        :return: AnalysisCard
        """
        item_type = body['item_type']

        from eureqa.analysis_cards import ModelCard,\
            DistributionPlotCard,\
            TextCard,\
            HtmlCard,\
            ModelFitByRowPlotCard,\
            ModelFitSeparationPlotCard,\
            ModelEvaluatorCard,\
            ModelSummaryCard,\
            BoxPlotCard,\
            DoubleHistogramPlotCard,\
            ScatterPlotCard,\
            BinnedMeanPlotCard,\
            ByRowPlotCard,\
            CustomPlotCard

        card_type_map = { x._item_type: x for x in [
            ModelCard,
            DistributionPlotCard,
            TextCard,
            HtmlCard,
            ModelFitByRowPlotCard,
            ModelFitSeparationPlotCard,
            ModelEvaluatorCard,
            ModelSummaryCard,
            BoxPlotCard,
            DoubleHistogramPlotCard,
            ScatterPlotCard,
            BinnedMeanPlotCard,
            ByRowPlotCard,
            CustomPlotCard
        ]}

        obj = card_type_map.get(item_type, cls)()

        obj._order = body.get('order_index')
        obj._body = body

        if eureqa:
            obj._eureqa = eureqa
        return obj

    @property
    def _channels(self):
        return [_Channel(x) for x in self._body.get('channels', [])]
    @_channels.setter
    def _channels(self, channels):
        self._body['channels'] = [x.name for x in channels]
        self._update_card()

    @property
    def _private_channel(self):
        # If we don't know our private channel, go search for it in our channels list
        if not hasattr(self, '_private_channel_obj'):
            for channel in getattr(self, '_channels', []):
                if channel.name.startswith("%s-" % self._id):
                    self._private_channel_obj = channel
                    break

        # If we still don't know our private channel, invent one
        if not hasattr(self, '_private_channel_obj'):
            self._private_channel_obj = _Channel(name_prefix = "%s-" % self._id)

        private_channel_obj = self._private_channel_obj

        if 'channels' not in self._body:
            self._body['channels'] = []
        if private_channel_obj.name not in self._body['channels']:
            self._body['channels'].append(private_channel_obj.name)
            self._update_card()
            # _update_card() erases self._private_channel_obj because it's
            # a local-only cache member variable.
            # We would regenerate it the next time we're called.
            # But, no need; we already know it, just set it again.
            self._private_channel_obj = private_channel_obj

        return private_channel_obj

    def replace(self, other):
        """ Replace this card's contents with the contents of `other`

        :param eureqa.analysis_card.AnalysisCard other: Card to replace our contents with
        """
        analysis_id = self._analysis_id
        id_ = self._id
        self.__init__(other._body, other._eureqa)
        self._body['item_id'] = id_
        self._id = id_
        self._body['analysis_id'] = analysis_id
        self._analysis_id = analysis_id
        self._update_card()

    def copy(self):
        """ Duplicates this AnalysisCard.
        If the current card is associated with an Analysis, the new card will not be associated with that Analysis
        and can be added to it or to any other Analysis.
        :return: A copy of this AnalysisCard.
        """
        body_copy = copy.deepcopy(self._body)
        if 'item_id' in body_copy:
            del body_copy['item_id']
        if 'analysis_id' in body_copy:
            del body_copy['analysis_id']
        return self.__class__.from_json(body_copy, getattr(self, '_eureqa', None))

    def delete(self):
        """Deletes the card from the server."""
        endpoint = '/analysis/%s/items/%s' % (self._analysis_id, self._id)
        self._eureqa._session.report_progress('Deleting card: \'%s\' from analysis: \'%s\'.' % (self._id, self._analysis_id))
        self._eureqa._session.execute(endpoint, 'DELETE')

    def _update_card(self):
        ## If we're not connected to an Analysis, there's nothing to update
        if not hasattr(self, '_eureqa') or not self._id or not self._analysis_id:
            return

        endpoint = '/analysis/%s/items/%s' % (self._analysis_id, self._id)
        self._eureqa._session.report_progress('Updating card: \'%s\' from analysis: \'%s\'.' % (self._id, self._analysis_id))
        new_body = self._eureqa._session.execute(endpoint, 'PUT', self.to_json())
        new_instance = self.__class__.from_json(new_body, self._eureqa)
        self.__dict__ = new_instance.__dict__

    def move_above(self, other_card):
        """Moves this card above another card.

        :param eureqa.analysis_cards.AnalysisCard other_card: The other card above which to move this card.
        """

        other_card_order = other_card._order if hasattr(other_card, '_order') else other_card
        if other_card_order >= self._order:
            return
        self._body['order_index'] = other_card_order
        self._update_card()

    def move_below(self, other_card):
        """Moves this card below another card.

        :param eureqa.analysis_cards.AnalysisCard other_card: The other card object below which to move this card.
        """

        other_card_order = other_card._order if hasattr(other_card, '_order') else other_card
        if other_card_order <= self._order:
            return
        self._body['order_index'] = other_card_order
        self._update_card()
