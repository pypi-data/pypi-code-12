import os.path

from .resource import List
from .resource import Find
from .resource import Create
from .resource import Post
from .resource import Update
from .resource import Delete
from .resource import Replace

from . import utils

THUMBNAIL_SIZES = 'sbtmlh'


class File(List, Find, Create, Post, Update, Delete, Replace):
    """Node class wrapping the REST nodes endpoint
    """
    path = "files"
    file_server_path = "file_storage/file"
    build_previews_server_path = "file_storage/build_previews"
    ensure_query_projections = {'backend': 1, 'file_path': 1, 'project': 1, 'content_type': 1,
                                'link': 1, 'link_expires': 1}

    def post_file(self, file_path, name=None, api=None):
        """Stores a file on the database or static folder.
        :param file: A file object
        """
        api = api or self.api
        url = utils.join_url(self.file_server_path)
        file_ = open(file_path, 'rb')
        files = {'data': file_}
        api.post(url, {"name": name}, {}, files)
        file_.close()
        # self.error = None
        # self.merge(new_attributes)
        return self.success()

    def build_previews(self, path, api=None):
        """Stores a file on the database or static folder.
        :param path: A file path
        """
        api = api or self.api
        url = utils.join_url(self.build_previews_server_path, path)
        api.get(url)
        return self.success()

    # def children(self, api=None):
    #     """Collect children (variations) of the current file. Used to connect
    #     different resolutions of the same picture, or multiple versions of the
    #     same video in different formats/containers.

    #     TODO: add params to support pagination.
    #     """
    #     api = api or self.api
    #     files = self.all({'where': '{"parent": "%s"}' % self._id}, api=api)
    #     if not files._items:
    #         return None
    #     return files

    def thumbnail(self, size, api=None):
        """Utility to replace a component of an image link so that it points to
        a thumbnail.
        """

        if size not in THUMBNAIL_SIZES:
            raise ValueError("Size should be in ({}), not {}"
                             .format(', '.join(THUMBNAIL_SIZES), size))

        if self.variations:
            thumbnail = next((item for item in self['variations']
                              if item['size'] == size), None)
            if thumbnail:
                return thumbnail['link']

        if self.link:
            root, ext = os.path.splitext(self.link)
            return "{0}-{1}.jpg".format(root, size)

        thumbnail = self.find_first({'where': {'parent': self._id, 'size': size}}, api=api)
        if thumbnail is not None:
            return thumbnail.link

        return ''

    def stream_thumb_to_file(self, directory, desired_size, api=None):
        """Streams a thumbnail to a file.

        @param directory: the directory to save the file to.
        @param desired_size: thumbnail size
        @return: the absolute path of the downloaded file.
        """

        api = api or self.api
        thumb_link = self.thumbnail(desired_size, api=api)

        if thumb_link is None:
            raise ValueError("File {} has no thumbnail of size {}"
                             .format(self._id, desired_size))

        root, ext = os.path.splitext(self.file_path)
        thumb_fname = "{0}-{1}.jpg".format(root, desired_size)

        # thumb is now a dict like:
        # {'content_type': 'image/jpeg', 'height': 160, 'length': 5846,
        #  'link': 'https://storage.googleapis.com/asdlajsdhaukihuwefiuh',
        #  'width': 160, 'size': 'b', 'file_path': '65b526639295c0dd9dc99cf54a0a606cd4924f1d-b.jpg',
        #  'md5': '--', 'format': 'jpg'},

        thumb_path = os.path.abspath(os.path.join(directory, thumb_fname))
        utils.download_to_file(thumb_link, thumb_path)

        return thumb_path
