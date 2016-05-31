from ubackup import settings
from ubackup import log
from uuid import uuid4
import mock
import os
import shutil
import unittest


def setUp(*args, **kwargs):
    log.set_config(settings.LOGGING)
    log.set_level('DEBUG')

    settings.CHUNK_SIZE = 100
    settings.CRYPT_KEY = "foo"
    settings.DROPBOX_TOKEN = "foo"
    settings.TMP_DIR = os.path.join(settings.CURRENT_DIR, ".tmp")
    settings.LOG_DIRECTORY = os.path.join(settings.TMP_DIR, "log_directory")

    class MockRequest(object):
        def json(*args, **kwargs):
            return {}

        @property
        def status_code(*args, **kwargs):
            return 200

    patcher = mock.patch('requests.request', return_value=MockRequest())
    patcher.start()

    settings.TMP_PATH = os.path.join(settings.CURRENT_DIR, '.tmp')
    os.mkdir(settings.TMP_PATH)


def tearDown(*args, **kwargs):
    shutil.rmtree(settings.TMP_PATH)


class TestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = self.create_tmp_dir()

    def create_tmp_dir(self):
        tmp_dir = os.path.join(settings.TMP_DIR, uuid4().hex)
        os.mkdir(tmp_dir)
        return tmp_dir

    def tmp_path(self):
        return os.path.join(self.tmp_dir, uuid4().hex)
