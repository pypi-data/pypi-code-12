from tcell_agent.policies.appsensor.sensor import sendEvent

class SizeSensor(object):
    MAX_NORMAL_REQUEST_BYTES = 1024*512
    DP_UNUSUAL_REQUEST_SIZE = "reqsz"

    def __init__(self, default_limit, dp_code, policy_json=None):
        self.enabled = False
        self.limit = default_limit
        self.exclude_routes = {}
        self.dp_code = dp_code

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)
            self.limit = policy_json.get("limit", self.limit)

            for route_id in policy_json.get("exclude_routes", []):
                self.exclude_routes[route_id] = True

    def check(self, appsensor_meta, str_length):
        if not self.enabled or self.exclude_routes.get(appsensor_meta.route_id, False):
            return

        if (str_length > self.limit):
            sendEvent(
              appsensor_meta,
              self.dp_code,
              str(str_length),
              None)

    def __str__(self):
        return "<%s enabled: %s limit: %s dp_code: %s exclude_routes: %s>" % \
            (type(self).__name__, self.enabled, self.limit, self.dp_code, self.exclude_routes)
