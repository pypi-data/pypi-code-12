from plugandpie.devices.Device import Device


class Accelerometer(Device):
    def __init__(self, interface):
        super().__init__(['accelerometer'], interface)

    def standby(self):
        raise NotImplementedError()

    def activate(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def set_g_range(self, g_range):
        raise NotImplementedError()

    def set_output_data_rate(self, output_data_rate):
        raise NotImplementedError()

    def get_ms2(self):
        raise NotImplementedError()

    def get_g(self):
        raise NotImplementedError()
