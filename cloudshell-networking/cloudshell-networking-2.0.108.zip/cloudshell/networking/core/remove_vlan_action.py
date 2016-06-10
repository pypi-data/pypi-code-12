# from CloudShell-Core.action_request import ActionRequest

class RemoveVlanAction(ActionRequest):
    def __init__(self):
        self.connectionId = ''
        self.connectorAttributes = []
