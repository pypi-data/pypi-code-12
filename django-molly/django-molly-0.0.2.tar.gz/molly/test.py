from django.core import wsgi
from heroin import test


class TestCase(test.TestCase):

    application = None

    def setUp(self):
        self.application = wsgi.WSGIHandler()
