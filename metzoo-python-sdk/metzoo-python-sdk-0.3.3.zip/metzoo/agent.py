# -*- coding: utf-8 -*-

import json
import metzoo
import requests
import time
import calendar

from .errors import AgentCreationError, AgentDataError, MetzooInvalidData

class Comparable(object):
    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        return not self.__ne__(other)


class RequestInfo(object):
    def __init__(self, method, route):
        self._method = method
        self._route = route

    @property
    def method(self):
        return self._method

    @property
    def route(self):
        return self._route


class Agent(Comparable):
    """Interface to communicate with metzoo services

    To create an agent just pass a name and your customer key:

        >>> agent = metzoo.Agent('xxx-xxx....', 'name')
        <Agent 'name', key: 'xxx-xxx...'>

    An agent is used to send data to metzoo:

        >>> agent.send({"single.metric": 123})
        {"status":"ok"}

        >>> agent.send({"multi.metric1": 123, "multi.metric2": 456})
        {"status":"ok"}

    You can send your own timestamp:

        >>> agent.send({"multi.metric1": 123, "multi.metric2": 456}, timestamp=789)
        {"status":"ok"}

    And can update it's own configuration:

        >>> agent.update()
    """

    REQ_INFO = \
            { "send": RequestInfo("POST", "/metrics/data")
            , "create": RequestInfo("POST", "/agents")
            , "set_unit": RequestInfo("PUT", "/metrics")
            }

    HEADERS = \
            { "Content-Type": "application/json"
            , "User-Agent": "metzoo-python-sdk/" + metzoo.__version__
            }

    def __init__(self, customer_key, name, url="http://api.metzoo.com"):
        """Initializes an agent for the given customer_key.

        If the agent doesn't exists it creates one.
        If it exists it load the configuration from metzoo servers.

        You can set the url to use your own api
        """

        assert customer_key is not None, "You must provide a customer key when creating an Agent"
        assert name is not None, "You must provide a name when creating an Agent"

        self.__customer_key = customer_key
        self.__name = name
        self.__url = url

    @property
    def name(self):
        """Returns the name of the agent"""
        return self.__name

    @property
    def url(self):
        """Returns the url of the api that the agent is communicating with"""
        return self.__url

    @property
    def customer_key(self):
        """Returns the customer key of the agent"""
        return self.__customer_key

    def configure(self, config):
        """It configures the agent, sets the unit for every metric

        config is a dict with metric names as keys and metric unit as value

        returns the response (as a json dict) of the request sent

        Example:
            >>> agent.configure({"metric.name": "Kilobytes", "metric.name2": "°C"})
            {"status":"ok"}
        """

        if type(config) is not dict:
            raise MetzooInvalidData(got=type(config), expected=dict)

        if len(config) == 0:
            raise MetzooInvalidData(got="an empty dict", expected="a dict with at least one key:value pair")

        units = []
        for metric in config:
            unit = config[metric]
            if type(unit) is not str:
                raise MetzooInvalidData(got=type(unit), expected="{} for the unit of {}".format(str, metric))
            units.append({"name": metric, "unit": unit})

        return self.__get_valid_response("set_unit", units, {"Customer-Key": self.__customer_key, "Host-Name": self.__name})

    def send(self, metrics, timestamp=None):
        """For every key-value pair in the dictionary metrics it will create the metric if it doesn't exists and it will
        send the data for that metric with the current timestamp

        metrics is a dict with metric names as keys and metric data as values

        timestamp is an optional parameter, if it's left as None, the timestamp sent is the result to
        calling calendar.timegm(time.gmtime()), but you can override this sending a value

        returns the response (as a json dict) of the request sent

        Example:
            >>> agent.send({"metric.name": 123})
            {"status":"ok"}

            >>> agent.send({"metric.name": 123}, timestamp=456)
            {"status":"ok"}

        """

        if type(metrics) is not dict:
            raise MetzooInvalidData(got=type(metrics), expected=dict)

        if len(metrics) == 0:
            raise MetzooInvalidData(got="an empty dict", expected="a dict with at least one key:value pair")

        if timestamp is None:
            timestamp = calendar.timegm(time.gmtime())
        else:
            self.__check_numeric_type(type(timestamp), "timestamp")

        data = {"t": timestamp}
        for metric in metrics:
            value = metrics[metric]
            self.__check_numeric_type(type(value), metric)
            data[metric] = value

        return self.__get_valid_response("send", data, {"Customer-Key": self.__customer_key, "Host-Name": self.__name})

    def update(self):
        """It downloads the configuration from metzoo server and update itself with it.
        """
        pass

    def __repr__(self):
        return "<Agent '%s'>" % (self.name)

    def __check_numeric_type(self, t, name):
        valid_types= [int, float, long, type(None)]
        if t not in valid_types:
            raise MetzooInvalidData(got=t, expected="{} type for {}".format(valid_types, name))

    def __request(self, info_name, body=None, headers={}):
        info = self.REQ_INFO[info_name]
        headers.update(self.HEADERS)
        response = requests.request(info.method, self.url + info.route, data=json.dumps(body), headers=headers)
        return (response.status_code, json.loads(response.text))

    def __get_valid_response(self, info_name, body, headers):
        status, response = self.__request(info_name, body, headers)
        if not status in range(200, 300):
            raise AgentDataError(status, response)
        return response
