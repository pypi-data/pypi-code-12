import unittest
import re

from tcell_agent.appsensor import params

EVIL_REGEX = re.compile("evil", flags=re.IGNORECASE|re.S|re.M)

def match_evil(param_name, param_value):
    return EVIL_REGEX.search(param_value)

class ParamsTest(unittest.TestCase):

    def test_param_for_simple_value(self):
        result = params.test_param("name", "evil value", match_evil)
        self.assertIsNotNone(result)
