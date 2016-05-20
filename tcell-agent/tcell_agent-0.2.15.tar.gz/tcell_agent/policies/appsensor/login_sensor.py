from tcell_agent.policies.appsensor.sensor import sendEvent
from tcell_agent.sanitize import SanitizeUtils

class LoginSensor(object):
    LOGIN_FAILURE_DP = "lgnFlr"

    def __init__(self, policy_json=None):
        self.enabled = False

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)

    def check(self, appsensor_meta, username):
        if not self.enabled:
            return

        if username is not None:
            username = SanitizeUtils.hmac(username)

        sendEvent(appsensor_meta, self.LOGIN_FAILURE_DP, username, payload=None)

    def __str__(self):
        return "<%s enabled: %s>" % (type(self).__name__, self.enabled)
