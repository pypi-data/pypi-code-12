from unittest import TestCase

from tests.test_integration import test_settings as settings
from yolapy.configuration import configure


# we have to configure before importing
configure(auth=settings.auth, url=settings.url)
from yolapy.services import Yola


class YolaServiceTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = Yola()
