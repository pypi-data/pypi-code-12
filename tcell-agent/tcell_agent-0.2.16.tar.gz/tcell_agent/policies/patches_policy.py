from tcell_agent.policies import TCellPolicy

import logging

logger = logging.getLogger('tcell_agent').getChild(__name__)

class PatchesPolicy(TCellPolicy):
    api_identifier = "patches"

    def __init__(self, policy_json=None):
        super(PatchesPolicy, self).__init__()
        self.policy_id = None
        self.version = None
        self.ip_blocking_enabled = False
        self.blocked_ips = {}

        if policy_json is not None:
            self.load_from_json(policy_json)
    def is_ip_blocked(self, ip_address):
        return self.ip_blocking_enabled and self.blocked_ips.get(ip_address, False)

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        if "version" in policy_json:
            self.version = policy_json["version"]

        if 1 is not self.version:
            logger.warn("Patches Policy not supported: %s" % self.version)
            return

        policy_data = policy_json.get("data")

        if policy_data:
            blocked_ips = policy_data.get("blocked_ips")
            if blocked_ips:
                for ip_info in blocked_ips:
                    if "ip" in ip_info:
                        self.ip_blocking_enabled = True
                        self.blocked_ips[ip_info["ip"]] = True

