import json

from tcell_agent.policies.appsensor.sensor import sendEvent

class DatabaseSensor(object):
    DP_CODE="dbmaxrows"

    def __init__(self, policy_json=None):
        self.enabled = False
        self.max_rows = 1001
        self.excluded_route_ids = {}

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)
            large_result = policy_json.get("large_result", {})
            self.max_rows = large_result.get("limit", self.max_rows)

            for route_id in policy_json.get("exclude_routes", []):
                self.excluded_route_ids[route_id] = True

    def check(self, appsensor_meta, number_of_records):
        if (not self.enabled) or self.excluded_route_ids.get(appsensor_meta.route_id, False):
            return

        if number_of_records > self.max_rows:
            sendEvent(
              appsensor_meta,
              self.DP_CODE,
              None,
              json.dumps({"rows": number_of_records}))

    def __str__(self):
        return "<%s enabled: %s max_rows: %s dp_code: %s excluded_route_ids: %s>" % \
            (type(self).__name__, self.enabled, self.max_rows, self.DP_CODE, self.excluded_route_ids)
