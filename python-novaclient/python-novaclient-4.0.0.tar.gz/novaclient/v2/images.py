# Copyright 2010 Jacob Kaplan-Moss
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
DEPRECATED: Image interface.
"""

import warnings

from six.moves.urllib import parse

from novaclient import base


class Image(base.Resource):
    """
    DEPRECATED: An image is a collection of files used to create or rebuild a
    server.
    """
    HUMAN_ID = True

    def __repr__(self):
        return "<Image: %s>" % self.name

    def delete(self):
        """
        DEPRECATED: Delete this image.

        :returns: An instance of novaclient.base.TupleWithMeta
        """
        return self.manager.delete(self)


class ImageManager(base.ManagerWithFind):
    """
    DEPRECATED: Manage :class:`Image` resources.
    """
    resource_class = Image

    def get(self, image):
        """
        DEPRECATED: Get an image.

        :param image: The ID of the image to get.
        :rtype: :class:`Image`
        """
        warnings.warn(
            'The novaclient.v2.images module is deprecated and will be '
            'removed after Nova 15.0.0 is released. Use python-glanceclient '
            'or python-openstacksdk instead.', DeprecationWarning)
        return self._get("/images/%s" % base.getid(image), "image")

    def list(self, detailed=True, limit=None, marker=None):
        """
        DEPRECATED: Get a list of all images.

        :rtype: list of :class:`Image`
        :param limit: maximum number of images to return.
        :param marker: Begin returning images that appear later in the image
                       list than that represented by this image id (optional).
        """
        warnings.warn(
            'The novaclient.v2.images module is deprecated and will be '
            'removed after Nova 15.0.0 is released. Use python-glanceclient '
            'or python-openstacksdk instead.', DeprecationWarning)
        params = {}
        detail = ''
        if detailed:
            detail = '/detail'
        if limit:
            params['limit'] = int(limit)
        if marker:
            params['marker'] = str(marker)
        params = sorted(params.items(), key=lambda x: x[0])
        query = '?%s' % parse.urlencode(params) if params else ''
        return self._list('/images%s%s' % (detail, query), 'images')

    def delete(self, image):
        """
        DEPRECATED: Delete an image.

        It should go without saying that you can't delete an image
        that you didn't create.

        :param image: The :class:`Image` (or its ID) to delete.
        :returns: An instance of novaclient.base.TupleWithMeta
        """
        warnings.warn(
            'The novaclient.v2.images module is deprecated and will be '
            'removed after Nova 15.0.0 is released. Use python-glanceclient '
            'or python-openstacksdk instead.', DeprecationWarning)
        return self._delete("/images/%s" % base.getid(image))

    def set_meta(self, image, metadata):
        """
        DEPRECATED: Set an images metadata

        :param image: The :class:`Image` to add metadata to
        :param metadata: A dict of metadata to add to the image
        """
        warnings.warn(
            'The novaclient.v2.images module is deprecated and will be '
            'removed after Nova 15.0.0 is released. Use python-glanceclient '
            'or python-openstacksdk instead.', DeprecationWarning)
        body = {'metadata': metadata}
        return self._create("/images/%s/metadata" % base.getid(image),
                            body, "metadata")

    def delete_meta(self, image, keys):
        """
        DEPRECATED: Delete metadata from an image

        :param image: The :class:`Image` to delete metadata
        :param keys: A list of metadata keys to delete from the image
        :returns: An instance of novaclient.base.TupleWithMeta
        """
        warnings.warn(
            'The novaclient.v2.images module is deprecated and will be '
            'removed after Nova 15.0.0 is released. Use python-glanceclient '
            'or python-openstacksdk instead.', DeprecationWarning)
        result = base.TupleWithMeta((), None)
        for k in keys:
            ret = self._delete("/images/%s/metadata/%s" %
                               (base.getid(image), k))
            result.append_request_ids(ret.request_ids)

        return result
