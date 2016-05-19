import tempfile
import unittest

from .video import FileName


class TestFileName(unittest.TestCase):

    def setUp(self):
        self.fixture_filepath = 'some_dir/20160329_cs_cs_25_1_virgins.avi'

    def test_init_from_filepath(self):
        fn = FileName(self.fixture_filepath)
        self.assertEqual(fn.filename, '20160329_cs_cs_25_1_virgins.avi')
        self.assertEqual(fn.date, '20160329')
        self.assertEqual(fn.female, 'cs')
        self.assertEqual(fn.male, 'cs')
        self.assertEqual(fn.info, '25')
        self.assertEqual(fn.id, '1')
        self.assertEqual(fn.extra, 'virgins')

    def test_init_from_fields(self):
        fn = FileName(
            date='20160329',
            female='cs',
            male='cs',
            info='25',
            id='1',
            extra='virgins'
        )
        self.assertEqual(fn.date, '20160329')
        self.assertEqual(fn.female, 'cs')
        self.assertEqual(fn.male, 'cs')
        self.assertEqual(fn.info, '25')
        self.assertEqual(fn.id, '1')
        self.assertEqual(fn.extra, 'virgins')

    def test_init_from_incomplete_fields(self):
        fn = FileName(
            date='20160329',
            info='25',
            id='1',
        )
        self.assertEqual(fn.date, '20160329')
        self.assertEqual(fn.female, '')
        self.assertEqual(fn.male, '')
        self.assertEqual(fn.info, '25')
        self.assertEqual(fn.id, '1')
        self.assertEqual(fn.extra, '')

    def test_init_without_arguments(self):
        with self.assertRaises(ValueError):
            FileName()

    def test_init_with_wrong_fields(self):
        fn = FileName(
            date='20160329',
            wrong='cs',
        )
        self.assertEqual(fn.date, '20160329')
        self.assertFalse(hasattr(fn, 'wrong'))

    def test_returned_fields(self):
        fn = FileName(self.fixture_filepath)
        expected = {
            'date': '20160329',
            'female': 'cs',
            'male': 'cs',
            'info': '25',
            'id': '1',
            'extra': 'virgins',
        }
        self.assertDictEqual(fn.fields(), expected)
