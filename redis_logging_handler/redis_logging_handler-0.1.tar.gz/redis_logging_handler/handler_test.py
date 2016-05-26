#!/usr/bin/env python

import unittest
import logging
from logging import config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(thread)d - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'redisHandler': {
            'level': 'DEBUG',
            'class': 'redis_logging_handler.handler.RedisHandler',
            'formatter': 'verbose',
            'host': '10.0.0.206',
            'port': 6395,
            'db': 8,
            'key': "test_redis_handler"
        }
    },
    'loggers': {
        'redis': {
            'level': 'DEBUG',
            'handlers': ['redisHandler'],
            'propagte': False,
        },
    },
}


class RedisHandlerTest(unittest.TestCase):

    def test_logger(self):
        config.dictConfig(LOGGING)
        log = logging.getLogger("redis")
        log.debug("test")


if __name__ == '__main__':
    unittest.main()
