from .appsensor_rule_manager import AppSensorRuleManager

import os.path
import sys
import json

import logging
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

rule_manager = AppSensorRuleManager()
try:
    basepath = os.path.dirname(__file__)
    baserulesfilename = os.path.abspath(os.path.join(basepath, "python-baserules.json"))
    rule_manager.load_rules_file(baserulesfilename)
except Exception as read_rules_exception:
    print(read_rules_exception)
    logging.debug(read_rules_exception)