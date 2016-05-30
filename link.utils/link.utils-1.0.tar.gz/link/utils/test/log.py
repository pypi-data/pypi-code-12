# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from b3j0f.conf import Configurable, category, Parameter
from link.utils.log import logrecord_to_dict
import logging


class TestConfigurableLogger(UTCase):
    def setUp(self):
        self.logger = logging.getLogger('link.utils.test.logging')

    def test_configurable(self):
        self.assertTrue(self.logger.__class__.__configurable__)

    def test_config_values(self):
        logconf = Configurable.get_annotations(self.logger)[0]

        expected_log_format = 'log'
        expected_log_level = 'debug'
        expected_log_filter = {'foo': 'bar'}

        conf = category(
            'LOGGING',
            Parameter(name='log_format', value=expected_log_format),
            Parameter(name='log_level', value=expected_log_level),
            Parameter(name='log_filter', value=expected_log_filter)
        )
        logconf.configure(conf=conf)

        self.assertEqual(self.logger.log_format, expected_log_format)
        self.assertEqual(self.logger.log_level, expected_log_level)
        self.assertEqual(self.logger.log_filter, expected_log_filter)


class TestLoggingUtils(UTCase):
    def setUp(self):
        self.record = logging.LogRecord(
            'link.utils.test.logging',
            logging.DEBUG,
            'link/utils/test/logging.py',
            38,
            'hello %s',
            ('world',),
            None,
            func='TestLoggingUtils'
        )

    def test_transformation(self):
        expected = {
            'name': 'link.utils.test.logging',
            'level': logging.DEBUG,
            'pathname': 'link/utils/test/logging.py',
            'lineno': 38,
            'msg': 'hello world',
            'func': 'TestLoggingUtils'
        }

        got = logrecord_to_dict(self.record)

        self.assertTrue(isinstance(got, dict))

        for key in expected:
            self.assertTrue(key in got)
            self.assertEqual(got[key], expected[key])


if __name__ == '__main__':
    main()
