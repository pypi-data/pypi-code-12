from tcell_agent.policies.appsensor.sensor import sendEvent

class UserAgentSensor(object):
    DP_CODE = "uaempty"

    def __init__(self, policy_json=None):
        self.enabled = False
        self.empty_enabled = False
        self.excluded_route_ids = {}

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)
            self.empty_enabled = policy_json.get("empty_enabled", False)

            for route_id in policy_json.get("exclude_routes", []):
                self.excluded_route_ids[route_id] = True

    def check(self, appsensor_meta):
        if not self.enabled or not self.empty_enabled:
            return

        if self.excluded_route_ids.get(appsensor_meta.route_id, False):
            return False

        if not(appsensor_meta.user_agent_str and appsensor_meta.user_agent_str.strip()):
            sendEvent(
              appsensor_meta,
              self.DP_CODE,
              None,
              None)

    def __str__(self):
        return "<%s enabled: %s empty_enabled: %s dp_code: %s>" % \
            (type(self).__name__, self.enabled, self.empty_enabled, self.DP_CODE)
