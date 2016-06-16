class ProtocolNotConfiguredException(Exception):
    def __init__(self, proto):
        super(ProtocolNotConfiguredException, self).__init__("The protocol: " + proto + " is not properly configured.")
