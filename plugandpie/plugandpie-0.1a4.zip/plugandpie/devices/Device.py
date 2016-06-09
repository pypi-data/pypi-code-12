from plugandpie.interfaces.Interface import Interface


class Device(object):
    def __init__(self, sensors, interface):
        self.sensors = sensors
        self.interface = interface

    def standby(self):
        raise NotImplementedError()

    def activate(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()
