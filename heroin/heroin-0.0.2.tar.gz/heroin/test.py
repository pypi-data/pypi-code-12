import django
import twisted


class TestCase(django.test.TestCase, twisted.trial.unittest.TestCase):
    pass
