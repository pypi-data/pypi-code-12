import unittest

from .storage import Storage

class StandardTests(unittest.TestCase):
    def get_driver(self):
        return None

    def ready_driver(self):
        pass

    def kill_driver(self):
        pass

    def setUp(self):
        self.driver = self.get_driver()
        self.ready_driver()

        if not self.driver:
            raise unittest.SkipTest('The driver is not defined.')

        self.storage = Storage(self.driver)

    def tearDown(self):
        self.kill_driver()

        del self.storage
        del self.driver

    def test_set_and_get_simple(self):
        self.storage.set('panda', 'something')
        self.assertEqual('something', self.storage.get('panda'))

    def test_set_and_get_document(self):
        expected = {
            'job':      'Detective',
            'location': 'London, UK',
        }

        self.storage.set('holmes', expected)
        self.assertEqual(expected['job'], self.storage.get('holmes')['job'])

    def test_set_twice(self):
        self.storage.set('panda', 'something')
        self.assertEqual('something', self.storage.get('panda'))

        self.storage.set('panda', 'python')
        self.assertEqual('python', self.storage.get('panda'))

    def test_get_nothing(self):
        self.assertEqual(None, self.storage.get('panda'))

    def test_remove_once(self):
        self.storage.set('panda', 'something')
        self.storage.remove('panda')

        self.assertEqual(None, self.storage.get('panda'))

    def test_remove_twice(self):
        self.storage.set('panda', 'something')
        self.storage.remove('panda')
        self.storage.remove('panda') # ensure that there is no error.

        self.assertEqual(None, self.storage.get('panda'))

    def test_dictionary_access(self):
        self.storage['panda'] = 'something'
        self.assertEqual('something', self.storage['panda'])

        del self.storage['panda']
        self.assertEqual(None, self.storage['panda'])
