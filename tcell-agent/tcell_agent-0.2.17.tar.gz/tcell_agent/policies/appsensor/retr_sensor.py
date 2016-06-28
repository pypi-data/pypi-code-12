from tcell_agent.policies.appsensor import InjectionSensor

class RetrSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(RetrSensor, self).__init__("retr", policy_json)
