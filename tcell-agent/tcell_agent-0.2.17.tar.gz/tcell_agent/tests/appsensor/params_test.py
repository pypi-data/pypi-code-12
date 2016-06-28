import unittest
import re

import logging
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)
from tcell_agent.appsensor import params

EVIL_REGEX = re.compile("evil", flags=re.IGNORECASE|re.S|re.M)

def match_evil(param_name, param_value):
    LOGGER.info("WILL TRY TO MATCH EVIL")
    LOGGER.info(param_name)
    LOGGER.info(param_value)
    LOGGER.info(EVIL_REGEX.search(param_value))
    LOGGER.info("WILL TRY TO MATCH EVIL")
    return EVIL_REGEX.search(param_value)

class ParamsTest(unittest.TestCase):

    def test_param_for_simple_value(self):
        LOGGER.info("LOGGING OUTPUT DOES SHOW UP")
        LOGGER.info(params.test_param)
        LOGGER.info("LOGGING OUTPUT DOES SHOW UP")
        result = params.test_param("name", "evil value", match_evil)
        self.assertIsNotNone(result)
