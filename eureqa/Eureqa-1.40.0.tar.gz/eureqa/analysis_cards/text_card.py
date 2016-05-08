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


class TextCard(AnalysisCard):
    """Represents a text card on the server.

    :param str title: Title of the card
    :param str description: Description of the card
    :param str text: Body of the card.  (Markdown-formatted text.)
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.TextCard.text: The card text.
    """
    _item_type = 'ANALYSIS_TEXT_BLOCK'

    def __init__(self, text='', title='Text', description=None, collapse=False):
        """ TextCard init """
        super(TextCard, self).__init__()

        self.title = title
        self.description = description
        self.text = text
        self.collapse = collapse

    @property
    def text(self):
        """The text contents of this card.

        :return: text contained in this card
        :rtype: str"""
        return self._body['content'].get('text', '')

    def __str__(self):
        """Get the text contents of this card.

        :return: text contained in this card
        :rtype: str"""
        return self.text

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

    def _get_images(self):
        """Get any images embedded in the text of this card

        Private for now to keep the public api simple

        :return: a list of all uploaded images referenced in the text of the card
        :rtype: :class:`~eureqa.utils.Image`
        """
        images = Image._get_images_from_text(self._eureqa, self.text)
        return images

    def delete(self):
        """Deletes the card from the server.

        If the card contains any images, they will be deleted.
        """
        for image in self._get_images():
            try:
                image.delete()
            except Exception as e:
                print "Caught exception in TextCard.delete:", e
        AnalysisCard.delete(self)
