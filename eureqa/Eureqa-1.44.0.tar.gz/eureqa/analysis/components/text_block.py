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
from eureqa.utils.image import Image

class TextBlock(_Component):

    _component_type_str = 'ANALYSIS_TEXT_BLOCK'

    def __init__(self, text='', analysis=None, component_id=None, component_type=None, description=None):
        if not text and description:
            "For backward compatibility"
            self._text = description
        else:
            self._text = text

        super(TextBlock, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def text(self):
        """Markdown-formatted text contents of this component

        :rtype: str"""
        return self._text

    @text.setter
    def text(self, val):
        self._text = val
        self._update()

    def delete(self):
        """Deletes the card from the server.

        If the card contains any images, they will be deleted.
        """
        for image in self._get_images():
            try:
                image.delete()
            except Exception as e:
                print "Caught exception in TextCard.delete:", e
        super(TextBlock, self).delete()

    def _get_images(self):
        """Get any images embedded in the text of this card

        Private for now to keep the public api simple

        :return: a list of all uploaded images referenced in the text of the card
        :rtype: :class:`~eureqa.utils.Image`
        """
        images = Image._get_images_from_text(self._analysis._eureqa, self.text)
        return images

    def _fields(self):
        return super(TextBlock, self)._fields() + [ 'text' ]

