from tcell_agent.appsensor.rules import rule_manager
from tcell_agent.policies.appsensor import InjectionSensor

class NullbyteSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(NullbyteSensor, self).__init__("null", policy_json)

    def get_ruleset(self):
        return rule_manager.get_ruleset_for("nullbyte")
