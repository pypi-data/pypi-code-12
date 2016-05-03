__author__ = 'dcortes'

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_utility_supplies_electricity import GatewayUtilitySuppliesElectricity
from dexma_api_v3.factory.utilities.supply import Supply


class RepositoryUtilitySuppliesElectricity(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewayUtilitySuppliesElectricity(endpoint)

    def _validate_supply(self, supply_dict):
        supply = Supply(supply_dict)
        supply.validate()
        return supply

    def get(self, token, id):
        supply_dict = self.gateway.get(token, id)
        return self._validate_supply(supply_dict)

    def fetch(self, token, parameters=None):
        supply_list = self.gateway.fetch(token, parameters)
        return [self._validate_supply(supply) for supply in supply_list]

    def save(self, token, device):
        status = self.gateway.save(token, device)
        return status