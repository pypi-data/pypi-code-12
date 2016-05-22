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
from eureqa.utils.image import Image

class HtmlCard(AnalysisCard):
    """** BETA **
    Represents a text card on the server.

    :param str title: Title of the card
    :param str description: Description of the card
    :param str html: Body of the card
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.HtmlCard.text: The card text.
    """
    _item_type = "ANALYSIS_HTML_BLOCK"

    def __init__(self, html='', title='HTML', description=None, collapse=False):
        """ HtmlCard init """
        super(HtmlCard, self).__init__()

        self.title = title
        self.description = description
        self.html = html
        self.collapse = collapse

    def __str__(self):
        """Get the text contents of this card.

        :return: text contained in this card
        :rtype: str"""
        return self.text

    @property
    def text(self):
        """The text contents of this card.

        :return: text contained in this card
        :rtype: str"""
        return self._body['content'].get('text', '')

    @text.setter
    def text(self, value):
        self._body['content']['text'] = value
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
    def html(self):
        """ The body of this card.

        :return: body of this card
        :rtype: str"""
        return self._body['content']['html']

    @html.setter
    def html(self, value):
        self._body['content']['html'] = value
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
