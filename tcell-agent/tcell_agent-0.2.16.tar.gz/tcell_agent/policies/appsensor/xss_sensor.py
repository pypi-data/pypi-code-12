from tcell_agent.policies.appsensor import InjectionSensor


class XssSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(XssSensor, self).__init__("xss", policy_json)

        self.libinjection = False

        if policy_json is not None:
            self.libinjection = policy_json.get("libinjection", False)
