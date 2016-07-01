# -*- coding: utf-8 -*-

import json
import requests
import time
import calendar

from urlparse import urlparse

from .utils import sanitize
from .functions import MetricFunction
from .errors import AgentCreationError, AgentDataError, MetzooInvalidData
from . import __version__


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
            , "functions": RequestInfo("POST", "/metrics/functions")
            }

    HEADERS = \
            { "Content-Type": "application/json"
            , "User-Agent": "metzoo-python-lib/" + __version__
            }

    def __init__(self, customer_key, name, url="http://api.metzoo.com"):
        """Initializes an agent for the given customer_key.

        If the agent doesn't exists it creates one.
        If it exists it load the configuration from metzoo servers.

        You can set the url to use your own api
        """

        result = urlparse(url)
        if len(result.scheme) == 0 and len(result.netloc) == 0:
            raise AgentCreationError(500, "Invalid URL")

        self.__customer_key = sanitize(customer_key, "customer_key", [str, unicode])
        if len(self.__customer_key) == 0:
            raise AgentCreationError(500, "You must provide a valid customer key, '{}' is not valid (type='{}')".format(customer_key, type(customer_key)))

        self.__name = sanitize(name, "name", [str, unicode])
        if len(self.__name) == 0:
            raise AgentCreationError(500, "You must provide a valid name, '{}' is not valid (type='{}')".format(name, type(name)))

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
            >>> agent.configure({"metric.name": "Kilobytes", "metric.name2": "°C})
            {"status":"ok"}
        """

        config = sanitize(config, "config", dict)

        if len(config) == 0:
            raise MetzooInvalidData(got="an empty dict", expected="a dict with at least one key:value pair")

        units = []
        for metric in config:
            unit = sanitize(config[metric], "unit of {}".format(metric), [str, unicode])
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

        metrics = sanitize(metrics, "metrics", dict)

        if len(metrics) == 0:
            raise MetzooInvalidData(got="an empty dict", expected="a dict with at least one key:value pair")

        data = {"t": sanitize(timestamp, "timestamp", [int, float, long, type(None)]) or calendar.timegm(time.gmtime())}
        for metric in metrics:
            data[metric] = sanitize(metrics[metric], "value of {}".format(metric), [int, float, long, type(None)])

        return self.__get_valid_response("send", data, {"Customer-Key": self.__customer_key, "Host-Name": self.__name})

    def register_function(self, function):
        return self.register_functions([function])

    def register_functions(self, functions):
        functions = sanitize(functions, "functions", list)
        functions = map(lambda x : sanitize(x[1], "function {}".format(x[0]), MetricFunction), enumerate(functions))
        return self.__get_valid_response("functions", map(MetricFunction.as_dict, functions), {"Customer-Key": self.__customer_key, "Host-Name": self.__name})

    def update(self):
        """It downloads the configuration from metzoo server and update itself with it.
        """
        pass

    def __repr__(self):
        return "<Agent '%s'>" % (self.name)

    def __request(self, info_name, body=None, headers={}):
        info = self.REQ_INFO[info_name]
        headers.update(self.HEADERS)
        response = requests.request(info.method, self.url + info.route, data=json.dumps(body), headers=headers)
        try:
            return (response.status_code, json.loads(response.text))
        except ValueError:
            return (response.status_code, response.text)

    def __get_valid_response(self, info_name, body, headers):
        status, response = self.__request(info_name, body, headers)
        if not status in range(200, 300):
            raise AgentDataError(status, response)
        return response
