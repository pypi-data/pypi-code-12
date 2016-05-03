__author__ = 'dcortes'

import arrow

from repository_base import RepositoryBase
from dexma_api_v3.gateway.gateway_cost_electrical_demand import GatewayCostElectricalDemand
from dexma_api_v3.factory.cost_electrical_factory.demand.multi_period import MULTI_PERIOD


class RepositoryCostElectricalDemand(RepositoryBase):

    def __init__(self, endpoint):
        self.gateway = GatewayCostElectricalDemand(endpoint)

    def _wrapper_cost_demand(self, consumption):
        if "type" not in consumption:
            raise Exception("undefined type of consumption")
        elif consumption["type"] == "MULTI_PERIOD":
            cons = MULTI_PERIOD(consumption, strict=False)
        else:
            raise Exception("type {} not allowed".format(consumption["type"]))
        cons.from_ = arrow.get(consumption["from"]).datetime
        for pos, period in enumerate(cons.periods):
            if period.price_change is not None:
                cons.periods[pos].price_change.from_ = arrow.get(consumption["periods"][pos]["price_change"]["from"]).datetime
        cons.validate()
        return cons

    def get(self, token, id):
        raise Exception("Method get not allowed by cost_electrical_factory, just go for fetch")

    def fetch(self, token, parameters=None):
        consumption_list = self.gateway.fetch(token, parameters)
        return [self._wrapper_cost_demand(consumption) for consumption in consumption_list]

    def save(self, token, location):
        raise Exception("Method save not allowed by readings, only fetch allowed")
