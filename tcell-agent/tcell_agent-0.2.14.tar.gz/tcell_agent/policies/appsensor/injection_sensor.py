import json
import re

from future.utils import iteritems
from tcell_agent.appsensor.params import test_param
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM
from tcell_agent.appsensor.rules import rule_manager
from tcell_agent.config import CONFIGURATION
from tcell_agent.policies.appsensor.sensor import sendEvent


SRE_MATCH_TYPE = type(re.match("",""))

class InjectionSensor(object):

    def __init__(self, dp, policy_json=None):
        self.enabled = False
        self.dp = dp
        self.exclude_headers = False
        self.exclude_forms = False
        self.exclude_cookies = False
        self.exclusions = {}
        self.active_pattern_ids = {}
        self.v1_compatability_enabled = False

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)
            self.exclude_headers = policy_json.get("exclude_headers", False)
            self.exclude_forms = policy_json.get("exclude_forms", False)
            self.exclude_cookies = policy_json.get("exclude_cookies", False)
            self.v1_compatability_enabled = policy_json.get("v1_compatability_enabled", False)

            for pattern in policy_json.get("patterns", []):
                self.active_pattern_ids[pattern] = True

            for common_word, locations in iteritems(policy_json.get("exclusions", {})):
                self.exclusions[common_word] = locations


    def create_payload(self, match, param_value):
        if match is None or param_value is None:
            return None
        if (isinstance(match, SRE_MATCH_TYPE) == False):
            return None
        return param_value

    def check(self, type_of_param, appsensor_meta, param_name, param_value):
        if self.exclude_forms and (GET_PARAM == type_of_param or POST_PARAM == type_of_param or JSON_PARAM == type_of_param):
            return False

        if self.exclude_cookies and COOKIE_PARAM == type_of_param:
            return False

        if self.enabled:
            vuln_results = self.is_vulnerable(param_name, param_value)

            if vuln_results:
                vuln_param = vuln_results.get("param")
                payload=None
                if vuln_param:
                    if CONFIGURATION.allow_unencrypted_appsensor_payloads:
                        if vuln_param.lower() in CONFIGURATION.blacklisted_params:
                            payload = "BLACKLISTED"

                        elif CONFIGURATION.whitelist_present and not(vuln_param.lower() in CONFIGURATION.whitelisted_params):
                             payload = "NOT_WHITELISTED"

                        else:
                            payload = self.create_payload(vuln_results.get("m"), vuln_results.get("value"))

                    sendEvent(
                        appsensor_meta,
                        self.dp,
                        vuln_param,
                        json.dumps({"t":type_of_param}),
                        payload,
                        vuln_results.get("pattern"))

                    return True

        return False

    def is_vulnerable(self, param_name, param_value):
        return test_param(param_name, param_value, self.check_dp_violation)

    def check_dp_violation(self, param_name, param_value):
        rules = self.get_ruleset()
        if rules:
            return rules.check_violation(param_name, param_value, self.active_pattern_ids, self.v1_compatability_enabled)
        return None

    def get_ruleset(self):
        return rule_manager.get_ruleset_for(self.dp)

    def __str__(self):
        return "<%s enabled: %s dp: %s exclude_headers: %s exclude_forms: %s exclude_cookies: %s v1_compatability_enabled: %s active_pattern_ids: %s exclusions: %s>" % \
            (type(self).__name__, self.enabled, self.dp, self.exclude_headers, self.exclude_forms, self.exclude_cookies, self.v1_compatability_enabled, self.active_pattern_ids, self.exclusions)
