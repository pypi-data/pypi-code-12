from tcell_agent.policies.appsensor import InjectionSensor

class CmdiSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(CmdiSensor, self).__init__("cmdi", policy_json)
