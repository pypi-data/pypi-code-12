import unittest
from datetime import timedelta

from s3_website import helper


class DurationConversionTest(unittest.TestCase):
    def test_duration_numeric(self):
        td = helper.timedelta_from_duration_string('600')
        self.assertEqual(td, timedelta(seconds=600))

    def test_duration_seconds(self):
        td = helper.timedelta_from_duration_string('10 seconds')
        self.assertEqual(td, timedelta(seconds=10))

    def test_duration_one_second(self):
        td = helper.timedelta_from_duration_string('1 second')
        self.assertEqual(td, timedelta(seconds=1))

    def test_duration_minutes(self):
        td = helper.timedelta_from_duration_string('45 minutes')
        self.assertEqual(td, timedelta(minutes=45))

    def test_duration_hours(self):
        td = helper.timedelta_from_duration_string('3 hours')
        self.assertEqual(td, timedelta(hours=3))

    def test_duration_days(self):
        td = helper.timedelta_from_duration_string('7 days')
        self.assertEqual(td, timedelta(days=7))

    def test_duration_months(self):
        td = helper.timedelta_from_duration_string('1 month')
        self.assertEqual(td, timedelta(days=30))

    def test_duration_years(self):
        td = helper.timedelta_from_duration_string('20 years')
        self.assertEqual(td, timedelta(days=(365 * 20)))

    def test_duration_composite(self):
        td = helper.timedelta_from_duration_string(
            '1 hour, 45 minutes, 30 seconds')
        self.assertEqual(td, timedelta(hours=1, minutes=45, seconds=30))

    def test_duration_invalid_negative(self):
        with self.assertRaises(ValueError):
            helper.timedelta_from_duration_string('-45 hours')


class PrefixTest(unittest.TestCase):
    def test_no_s3_prefix(self):
        name = helper.add_s3_prefix('some_bucket_name')
        self.assertEqual(name, 's3://some_bucket_name')

    def test_with_s3_prefix(self):
        name = helper.add_s3_prefix('s3://some_bucket_name')
        self.assertEqual(name, 's3://some_bucket_name')

    def test_no_cf_prefix(self):
        name = helper.add_cf_prefix('some_bucket_name')
        self.assertEqual(name, 'cf://some_bucket_name')

    def test_with_cf_prefix(self):
        name = helper.add_cf_prefix('cf://some_bucket_name')
        self.assertEqual(name, 'cf://some_bucket_name')

    def test_no_prefix(self):
        name = helper.prefix('some_bucket_name', 'prefix')
        self.assertEqual(name, 'prefixsome_bucket_name')

    def test_with_prefix(self):
        name = helper.prefix('prefixsome_bucket_name', 'prefix')
        self.assertEqual(name, 'prefixsome_bucket_name')
