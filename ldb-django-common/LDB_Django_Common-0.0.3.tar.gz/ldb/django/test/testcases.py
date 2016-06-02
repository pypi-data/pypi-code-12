from django.test.utils import override_settings
from django.test import LiveServerTestCase

import tempfile
import shutil
import urlparse

class MediaSandboxTestMixin(object):
    # TODO: Handle exceptions (call teardown or w/e needs to happen)
    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._media_context = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_context.enable()
        super(MediaSandboxTestMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(MediaSandboxTestMixin, cls).tearDownClass()
        cls._media_context.disable()
        shutil.rmtree(cls._media_root)


class SeleniumTestCase(LiveServerTestCase):
    # TODO: Handle exceptions (call teardown or w/e needs to happen)
    @classmethod
    def setUpClass(cls):
        from selenium import webdriver

        super(SeleniumTestCase, cls).setUpClass()
        cls.selenium = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    @classmethod
    def make_url(cls, rel_address):
        return urlparse.urljoin(cls.live_server_url, rel_address)

    @classmethod
    def selenium_get(cls, rel_address):
        cls.selenium.get(cls.make_url(rel_address))
