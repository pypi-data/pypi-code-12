from tcell_agent.policies.appsensor import InjectionSensor

class FptSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(FptSensor, self).__init__("fpt", policy_json)
