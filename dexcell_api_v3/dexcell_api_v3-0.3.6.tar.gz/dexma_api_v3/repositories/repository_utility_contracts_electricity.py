__author__ = 'dcortes'

import arrow

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_utility_contract_electricity import GatewayUtilityContractElectricity
from dexma_api_v3.factory.utilities.contract_electrical import ContractElectrical


class RepositoryUtilityContractsElectricity(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewayUtilityContractElectricity(endpoint)

    def _validate_contract(self, supply_dict):
        contract = ContractElectrical(supply_dict, strict=False)
        contract["from_"] = arrow.get(supply_dict["from"]).datetime
        contract.validate()
        return contract

    def get(self, token, id):
        pass

    def fetch(self, token, parameters=None):
        contract_list = self.gateway.fetch(token, parameters)
        return [self._validate_contract(contract) for contract in contract_list]

    def save(self, token, device):
        pass