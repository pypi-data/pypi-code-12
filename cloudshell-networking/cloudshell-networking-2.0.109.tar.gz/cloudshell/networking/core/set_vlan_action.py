from CloudShell-Core.action_request import ActionRequest
from set_vlan_parameters import SetVlanParameters

class SetVlanAction(ActionRequest):
    def __init__(self):
        self.connectionId = ''
        self.connectionParams = SetVlanParameters()
        self.connectorAttributes = []
