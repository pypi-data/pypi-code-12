from tcell_agent.policies.appsensor import SizeSensor

class RequestSizeSensor(SizeSensor):
    MAX_NORMAL_REQUEST_BYTES = 1024*512
    DP_UNUSUAL_REQUEST_SIZE = "reqsz"

    def __init__(self, policy_json=None):
        super(RequestSizeSensor, self).__init__(
            self.MAX_NORMAL_REQUEST_BYTES,
            self.DP_UNUSUAL_REQUEST_SIZE,
            policy_json
        )
