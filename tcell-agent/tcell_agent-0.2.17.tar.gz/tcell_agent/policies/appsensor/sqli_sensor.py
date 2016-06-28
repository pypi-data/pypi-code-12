from tcell_agent.policies.appsensor import InjectionSensor

class SqliSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(SqliSensor, self).__init__("sqli", policy_json)

        self.libinjection = False

        if policy_json is not None:
            self.libinjection = policy_json.get("libinjection", False)
