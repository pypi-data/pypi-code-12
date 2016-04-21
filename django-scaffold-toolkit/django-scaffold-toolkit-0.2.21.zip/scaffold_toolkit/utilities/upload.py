# coding=utf-8
import json
import os
import datetime

from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.cache import cache
from django.utils.deconstruct import deconstructible
import shortuuid


@deconstructible
class UploadTo(object):
    def __init__(self, sub_path, fmt, rename=True):
        self.path = sub_path
        self.fmt = fmt
        self.rename = rename

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1]

        today = datetime.datetime.today()

        name = '%s%s' % (shortuuid.uuid(), ext.lower()) if self.rename else filename

        return os.path.join(self.path, today.strftime(self.fmt), name)


# class who handles the upload
class ProgressUploadHandler(TemporaryFileUploadHandler):
    """
    Download the file and store progression in the cache
    """

    def __init__(self, request=None):
        super(ProgressUploadHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None
        self.request = request

    def new_file(self, file_name, *args, **kwargs):
        content_length = self.content_length
        super(ProgressUploadHandler, self).new_file(file_name, *args, **kwargs)
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in self.request.META:
            self.progress_id = self.request.META['X-Progress-ID']
        if self.progress_id:
            self.cache_key = self.progress_id
            progress_data = json.loads(cache.get('upload_progress_%s' % self.cache_key, '{}'))
            progress_data.update({
                self.field_name: {
                    'length': content_length,
                    'field_name': self.field_name,
                    'uploaded': 0
                }
            })
            cache.set('upload_progress_%s' % self.cache_key, json.dumps(progress_data))

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length

    def receive_data_chunk(self, raw_data, start):
        if self.progress_id:
            progress_data = json.loads(cache.get('upload_progress_%s' % self.cache_key, "{}"))
            data = progress_data[self.field_name]
            data['uploaded'] += self.chunk_size
            cache.set('upload_progress_%s' % self.cache_key, json.dumps(progress_data))

        # data wont be passed to any other handler
        super(ProgressUploadHandler, self).receive_data_chunk(raw_data, start)

    def file_complete(self, file_size):
        if self.progress_id and 'upload_progress_%s' % self.cache_key in cache:
            progress_data = json.loads(cache.get('upload_progress_%s' % self.cache_key))
            progress_data.pop(self.field_name)
            if progress_data:
                cache.set('upload_progress_%s' % self.cache_key, json.dumps(progress_data))
            else:
                cache.delete('upload_progress_%s' % self.cache_key)

        return super(ProgressUploadHandler, self).file_complete(file_size)
