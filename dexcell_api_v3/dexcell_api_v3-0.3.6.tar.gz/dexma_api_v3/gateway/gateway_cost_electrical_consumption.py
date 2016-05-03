__author__ = 'dcortes'

from datetime import datetime
from dateutil.relativedelta import relativedelta
from copy import deepcopy

import arrow

from gateway_base import GatewayBase


class GatewayCostElectricalConsumption(GatewayBase):

    def __init__(self, endpoint, http_management=None):
        call = "cost/electrical/consumption"
        super(GatewayCostElectricalConsumption, self).__init__(endpoint, call, http_management=http_management)

    def get(self, token, id):
        raise Exception("Method get not allowed by readings, just go for fetch")
    def _get_nice_timestamps(self, date):
        return date.strftime("%Y-%m-%dT%H:%M:%S")

    def _basic_fetch(self, token, parameters, list_consumption):
        params = deepcopy(parameters)
        params["from"] = self._get_nice_timestamps(params["from"])
        params["to"] = self._get_nice_timestamps(params["to"])
        new_consumption = super(GatewayCostElectricalConsumption, self).fetch(token, params)
        list_consumption.extend(new_consumption)
        return list_consumption

    def _loop_fetch(self, token, parameters, interval):
        list_consumption = []
        while parameters["from"] + interval < parameters["to"]:
            list_consumption = self._basic_fetch(token, parameters, list_consumption)
            parameters["from"] += interval
        return self._basic_fetch(token, parameters, list_consumption)

    def _fetch_year(self, token, parameters):
        # for ten, quarter, half and hourly frequency
        return self._loop_fetch(token, parameters, relativedelta(years=1))

    def _fetch_ten_years(self, token, parameters):
        # for daily, weekly and monthly frequency
        return self._loop_fetch(token, parameters, relativedelta(years=10))

    def fetch(self, token, parameters=None):
        if "device_id" not in parameters or type(parameters["device_id"]) not in [int, long]: raise Exception("needed parameter device as int")
        if "from" in parameters and type(parameters["from"]) in [str, unicode]: parameters["from"] = arrow.get(parameters["from"]).datetime
        if "to" in parameters and type(parameters["to"]) in [str, unicode]: parameters["to"] = arrow.get(parameters["to"]).datetime
        if "from" not in parameters or type(parameters["from"]) != datetime: raise Exception("needed parameter from as datetime")
        if "to" not in parameters or type(parameters["to"]) != datetime: raise Exception("needed parameter to as datetime")
        if "resolution" not in parameters: raise Exception("needed parameter resolution as string")

        if parameters["resolution"] in ["QH", "HH", "H"]: return self._fetch_year(token, parameters)
        if parameters["resolution"] in ["D", "W", "M"]: return self._fetch_ten_years(token, parameters)
        else: raise Exception("resolution not in the list (QH, HH, H, D, W, M)")

    def save(self, token, location):
         raise Exception("Method save not allowed by readings, just go for fetch")
