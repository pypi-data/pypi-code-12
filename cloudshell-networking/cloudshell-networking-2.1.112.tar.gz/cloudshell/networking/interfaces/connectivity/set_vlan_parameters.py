import enum
from access_mode import AccessMode


class SetVlanParameters(object):
    def __init__(self):
        self.type = ''
        self.vlanIds = []
        self.mode = AccessMode.Access


