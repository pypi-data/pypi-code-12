
from django.test import TestCase
from testapp.models import Thing

class CommandTests(TestCase):
    fixtures = ['test-data']

    def test_fixture(self):
        self.assertEqual(Thing.objects.get(name='A').name, 'A')

    def test_create(self):
        Thing.objects.create(name='E')
        self.assertEqual(Thing.objects.get(name='E').name, 'E')

    test_recreate = test_create

CopyTests = CommandTests

