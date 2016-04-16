from django.test import TestCase as DjangoTestCase
from twisted.trial.unittest import TestCase as TwistedTestCase


class TestCase(DjangoTestCase, TwistedTestCase):
    pass
