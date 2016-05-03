__author__ = 'dcortes'

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_device import GatewayDevice
from dexma_api_v3.factory.device import Device


class RepositoryDevice(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewayDevice(endpoint)

    def _validate_device(self, device_dict):
        device = Device(device_dict)
        device.validate()
        return device

    def get(self, token, id):
        device_dict = self.gateway.get(token, id)
        return self._validate_device(device_dict)

    def fetch(self, token, parameters=None):
        device_dict = self.gateway.fetch(token, parameters)
        return [self._validate_device(dev) for dev in device_dict]

    def save(self, token, device):
        status = self.gateway.save(token, device)
        return status