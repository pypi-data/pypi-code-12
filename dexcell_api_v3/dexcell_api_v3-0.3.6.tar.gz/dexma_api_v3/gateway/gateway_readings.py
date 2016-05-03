__author__ = 'dcortes'

from datetime import datetime
from dateutil.relativedelta import relativedelta
from copy import deepcopy

from gateway_base import GatewayBase


class GatewayReadings(GatewayBase):

    def __init__(self, endpoint, http_management=None):
        call = "readings"
        super(GatewayReadings, self).__init__(endpoint, call, http_management=http_management)

    def get(self, token, id):
        raise Exception("Method get not allowed by readings, just go for fetch")

    def _get_nice_timestamps(self, date):
        return date.strftime("%Y-%m-%dT%H:%M:%S")

    def _basic_fetch(self, token, parameters, interval, readings):
        params = deepcopy(parameters)
        params["from"] = self._get_nice_timestamps(params["from"])
        params["to"] = self._get_nice_timestamps(params["to"])
        reads = super(GatewayReadings, self).fetch(token, params)
        if readings == {}: return reads
        else: readings["values"].extend(reads["values"])
        return readings

    def _loop_fetch(self, token, parameters, interval):
        readings = {}
        while parameters["from"] + interval < parameters["to"]:
            readings = self._basic_fetch(token, parameters, interval, readings)
            parameters["from"] += interval
        return self._basic_fetch(token, parameters, interval, readings)

    def _fetch_month(self, token, parameters):
        # for basic and five minutes frequency
        return self._loop_fetch(token, parameters, relativedelta(months=1))

    def _fetch_year(self, token, parameters, call):
        # for ten, quarter, half and hourly frequency
        return self._loop_fetch(token, parameters, relativedelta(years=1))

    def _fetch_ten_years(self, token, parameters):
        # for daily, weekly and monthly frequency
        return self._loop_fetch(token, parameters, relativedelta(years=10))

    def fetch(self, token, parameters=None):
        if "device_id" not in parameters or type(parameters["device_id"]) not in [int, long]: raise Exception("needed parameter device as int")
        if "from" not in parameters or type(parameters["from"]) != datetime: raise Exception("needed parameter from as datetime")
        if "to" not in parameters or type(parameters["to"]) != datetime: raise Exception("needed parameter to as datetime")
        if "resolution" not in parameters: raise Exception("needed parameter resolution as string")
        if "parameter_key" not in parameters: raise Exception("needed parameter parameter_key as string")

        if parameters["resolution"] in ["FM", "B"]: return self._fetch_month(token, parameters)
        if parameters["resolution"] in ["TM", "QH", "HH", "H"]: return self._fetch_year(token, parameters)
        if parameters["resolution"] in ["D", "W", "M"]: return self._fetch_ten_years(token, parameters)
        else: raise Exception("resolution not in the list (B, FM, TM; QH, HH, H, D, W, M)")


    def save(self, token, location):
        """ #TODO """
        return
