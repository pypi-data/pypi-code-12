from __future__ import absolute_import

import os
import logging.config

import yaml

from .config import get_config_paths

SCRIPT_DIR = os.path.dirname(__file__)


# http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
def setup_logging():
    """
    Setup logging configuration
    """
    for path in list(get_config_paths(filename='logconfig.yml'))[-1::-1]:
        if not os.path.exists(path):
            continue

        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())

        LOG_LEVEL = os.environ.get('LOG_LEVEL')
        if LOG_LEVEL:
            config['root']['level'] = LOG_LEVEL.upper()
            config['handlers']['console']['level'] = LOG_LEVEL.upper()

        logging.config.dictConfig(config)
