__author__ = 'dcortes'

import arrow

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_cost_electrical_summary import GatewayCostElectricalSummary
from dexma_api_v3.factory.cost_electrical_factory.summary import Summary
from dexma_api_v3.factory.device import Device
from dexma_api_v3.factory.utilities.price_electrical import PriceElectrical


class RepositoryCostElectricalSummary(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewayCostElectricalSummary(endpoint)

    def _check_internal_entity(self, embedded, type, entity, summary):
        if type in embedded:
            subentity = entity(summary[type])
            subentity.validate()

    def _wrapper_cost_summary(self, summary_dict, embedded):
        summary = Summary(summary_dict, strict=False)
        self._check_internal_entity(embedded, "prices", PriceElectrical, summary)
        self._check_internal_entity(embedded, "device", Device, summary)
        summary.from_ = arrow.get(summary_dict["from"]).datetime
        summary.validate()
        return summary

    def get(self, token, id):
        raise Exception("Method get not allowed by cost_electrical_factory, just go for fetch")

    def fetch(self, token, parameters=None):
        summary_list = self.gateway.fetch(token, parameters)
        embedded = parameters.get("embed", []) if parameters is not None else []
        return [self._wrapper_cost_summary(summary, embedded) for summary in summary_list]

    def save(self, token, location):
        raise Exception("Method save not allowed by cost summary, only fetch allowed")
