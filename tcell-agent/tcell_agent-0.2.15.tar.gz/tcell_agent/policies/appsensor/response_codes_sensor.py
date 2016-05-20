from tcell_agent.policies.appsensor.sensor import sendEvent

class ResponseCodesSensor(object):
    RESPONSE_CODE_DP_DICT = {
        401:"s401",
        403:"s403",
        404:"s404",
        4:"s4xx",
        500:"s500",
        5:"s5xx"
    }

    def __init__(self, policy_json=None):
        self.enabled = False
        self.series_400_enabled = False
        self.series_500_enabled = False

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)
            self.series_400_enabled = policy_json.get("series_400_enabled", False)
            self.series_500_enabled = policy_json.get("series_500_enabled", False)

    def check(self, appsensor_meta, response_code):
        if not self.enabled:
            return

        if response_code == 200:
            return
        if not self.series_400_enabled and (response_code >= 400 and response_code < 500):
            return
        if not self.series_500_enabled and (response_code >= 500 and response_code < 600):
            return

        dp = self.RESPONSE_CODE_DP_DICT.get(response_code)
        if dp is None:
            code_series = int(response_code / 100)
            dp = self.RESPONSE_CODE_DP_DICT.get(code_series)

        if dp:
            sendEvent(
              appsensor_meta,
              dp,
              str(response_code),
              None)

    def __str__(self):
        return "<%s enabled: %s series_400_enabled: %s series_500_enabled: %s>" % \
            (type(self).__name__, self.enabled, self.series_400_enabled, self.series_500_enabled)
