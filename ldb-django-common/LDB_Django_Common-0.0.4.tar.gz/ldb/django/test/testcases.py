from django.test.utils import override_settings
from django.test import LiveServerTestCase

from django.conf import global_settings

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


class DjangoAppTestCaseMixin(object):
    applications = []
    pre_middleware = []
    post_middleware = []

    @classmethod
    def setUpClass(cls):
        settings = {'DEBUG': True,
                    'SECRET_KEY': 'fake_key',
                    'INSTALLED_APPS': cls.get_applications(),
                    'ROOT_URLCONF': cls.root_urlconf,
                    'STATIC_URL': '/static/',
                    'MEDIA_ROOT': None,
                    'LOGGING': {
                        'version': 1,
                        'disable_existing_loggers': True,
                        'handlers': {
                            'console': {
                                'level': 'INFO',
                                'class': 'logging.StreamHandler'
                            }
                        },
                        'loggers': {
                            'django.request': {
                                'handlers': ['console'],
                                'propogate': True
                            }
                        }
                    },
                    'MIDDLEWARE_CLASSES': cls.get_middleware()
                   }
        cls.__settings_context = override_settings(**settings)
        cls.__settings_context.enable()

        super(DjangoAppTestCaseMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(DjangoAppTestCaseMixin, cls).tearDownClass()

        cls.__settings_context.disable()

    @classmethod
    def get_applications(cls):
        return global_settings.INSTALLED_APPS + list(cls.applications)

    @classmethod
    def get_middleware(cls):
        return (list(cls.pre_middleware) + global_settings.MIDDLEWARE_CLASSES +
                list(cls.post_middleware))


class DjangoSessionAppTestCaseMixin(DjangoAppTestCaseMixin):
    @classmethod
    def get_applications(cls):
        return (super(DjangoSessionAppTestCaseMixin, cls).get_applications() + 
                ['django.contrib.sessions'])

    @classmethod
    def get_middleware(cls):
        return (super(DjangoSessionAppTestCaseMixin, cls).get_middleware() + 
                ['django.contrib.sessions.middleware.SessionMiddleware'])


class DjangoContentTypeAppTestCaseMixin(DjangoAppTestCaseMixin):
    @classmethod
    def get_applications(cls):
        return (super(DjangoContentTypeAppTestCaseMixin,
                      cls).get_applications() + 
                ['django.contrib.contenttypes'])


class DjangoAuthAppTestCaseMixin(DjangoSessionAppTestCaseMixin,
                                 DjangoContentTypeAppTestCaseMixin):
    @classmethod
    def get_applications(cls):
        return (super(DjangoAuthAppTestCaseMixin, cls).get_applications() + 
                ['django.contrib.auth'])

    @classmethod
    def get_middleware(cls):
        return (super(DjangoAuthAppTestCaseMixin, cls).get_middleware() + 
                ['django.contrib.auth.middleware.AuthenticationMiddleware'])
