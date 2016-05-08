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

import re
import os
from objectstore import ObjectStore

class Image:
    """Represents an image which has been uploaded to the server

    :param Eureqa eureqa: A eureqa connection.
    :param str image_filename: The name of the image file.
    :param str image_key: The identifying key of the image file in the objectstore image_uploads bucket.
    """

    def __init__(self, eureqa, image_filename, image_key):
        """Represents an image stored on the server.
        """

        self._eureqa = eureqa
        self._filename = image_filename
        self._key = image_key

    """For internal use only. ObjectStore bucket in which images are stored."""
    _image_bucket = 'image_uploads'

    @property
    def image_filename(self): return self._filename

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               self._filename == other._filename and \
               self._key == other._key

    def __ne__(self, other): return not self.__eq__(other)

    def __str__(self):
        """Get the markup text used to embed this image in an analysis `~TextCard`.

        :return: markup text
        :rtype: str
        """

        # get fully qualified uri of the form '/api/v2/:org/objstore/image_uploads/:image_key'
        image_text = '![%s](%s)' % (self.image_filename, self._web_url)
        return image_text

    @property
    def _python_url(self):
        # get fully qualified uri of the form '/api/v2/:org/objstore/image_uploads/:image_key'
        return ObjectStore.construct_python_uri_full(self._eureqa._session.organization, self._image_bucket, self._key)

    @property
    def _web_url(self):
        # get fully qualified uri of the form '/api/:org/objstore/image_uploads/:image_key'
        return ObjectStore.construct_uri_full(self._eureqa._session.organization, self._image_bucket, self._key)

    @classmethod
    def upload_from_file(cls, eureqa, image_path):
        """Uploads an image from file.

        :param str cls: Classpath object. 
        :param Eureqa eureqa: A eureqa connection.
        :param str image_path: The path to an image file.
        :return: An Image object representing the newly uploaded image.
        :rtype: :class:`eureqa.utils.Image`
        """

        objectstore = ObjectStore(eureqa)

        filename = os.path.basename(image_path)
        response = objectstore.put(cls._image_bucket, filepath=image_path)
        key = response['key']
        return Image(eureqa, filename, key)

    def _download(self, image_path):
        """Download the image file to disk.

        Private for now to keep the public api simple

        :param str image_path: where to save the image file. Should be full filepath, not directory.
        """

        objectstore = ObjectStore(self._eureqa)
        response = objectstore.get(self._image_bucket, self._key, filepath=image_path)

    def delete(self):
        """Removes the image from the server. Caller is expected to throw away this object afterwards.
        """

        objectstore = ObjectStore(self._eureqa)
        response = objectstore.delete(self._image_bucket, self._key)

    @classmethod
    def _get_images_from_text(cls, eureqa, text):
        """Given some text, get a list of `~Image` objects representing all the images embedded in the text.

        Private for now to keep the public api simple

        :param str text: markup text which may contain references to images.
        :return: a list of image objects in the order in which they appear.
        :rtype: list of :class:`~eureqa.utils.Image`
        """

        # extract the file names and uris of any embedded images in the card text.
        # Image embeds are of the form ![Image Filename.xxx](/api/v2/:org/objstore/image_uploads/:image_key).
        # So this regex has two groups. First group captures the filename, and second captures the image
        # uri
        regex_result = re.findall('\!\[([^\[^\]]*)\]\(/api([^\(^\)]*)\)', text)
        # since regex has two groups, result is of the form [('filename1','uri1'),('filename2','uri2'),...]
        # we also extract the image keys from the image uris by getting the last part of the uri
        images = [Image(eureqa, filename, ObjectStore.get_uri_parts(uri)[-1]) for filename, uri in regex_result]
        return images
