# -*- coding: utf-8 -*-

import yaml
import OpenOPC
import metzoo
import logging
import itertools
from operator import itemgetter

from .data import OPCData

class ___BAD_CLASS___(object):
    pass

___BAD___ = ___BAD_CLASS___()


class Config(object):
    def __init__(self, config_dict):
        if type(config_dict) is not dict:
            raise TypeError("got {} expected {}".format(type(config_dict), dict))
        self.__dict = config_dict

    def get(self, name, default=___BAD___):
        keys = name.split(".")
        data = self.__dict
        try:
            for key in keys:
                data = data[key]
        except KeyError:
            if default is ___BAD___:
                raise
            data = default
        return data


class YAMLConfig(Config):
    def __init__(self, yaml_filename):
        with open(yaml_filename) as f:
            super(YAMLConfig, self).__init__(yaml.load(f))


class MetzooOPC(object):
    def __init__(self, config):
        self.__validate_config(config)
        self.__config = config
        self.__opc = None

    def __del__(self):
        try:
            self.__opc.close()
        except:
            pass

    @property
    def use_opc_time(self):
        return self.__config.get("use_opc_time", False)

    @property
    def timeformat(self):
        return self.__config.get("time_format", None)

    @property
    def url(self):
        return self.__config.get("metzoo.url", None)

    @property
    def customer_key(self):
        return self.__config.get("metzoo.customer_key", None)

    @property
    def mapping(self):
        return self.__config.get("opc.mapping", None)

    def read(self):
        from time import gmtime
        from calendar import timegm
        from datetime import datetime
        data_list = []
        for (tag, value, quality, timestamp) in self._opc.read(self.mapping.keys()):
            t = timegm(gmtime())
            if self.use_opc_time and self.timeformat is not None:
                t = timegm(datetime.strptime(timestamp, self.timeformat).timetuple())
            data_list.append(OPCData(None, tag, value, quality, t, self.mapping))
        return data_list

    def send(self, data_list):
        good = []
        bad = []
        data_sorted= sorted(data_list, key=itemgetter('timestamp', 'agent')) 
        for key, group in itertools.groupby(data_sorted, key=lambda x:{"timestamp": x.timestamp, "agent": x.agent}):
            elements= []
            try:
                data= {"t": key["timestamp"]}
                for item in group:
                    if item.quality == "Good":
                        data[item.metric]= item.value
                        elements.append(item)
                    else:
                        bad.append(item)
                agent= metzoo.Agent(self.customer_key, key["agent"], self.url)
                agent.send(data)
            except Exception as ex:
                logging.warn("can't send data: {}".format(ex))
                for item in elements:
                    bad.append(item)
            else:
                for item in elements:
                    good.append(item)
        return good, bad

    def __validate_config(self, config):
        if not isinstance(config, Config):
            raise TypeError("got {} expected {}".format(type(config), Config))

        self.__validate_config_property_type(config, "use_opc_time", bool)
        self.__validate_config_property_type(config, "time_format", str)
        self.__validate_config_property_type(config, "metzoo", dict)
        self.__validate_config_property_type(config, "metzoo.customer_key", str)
        self.__validate_config_property_type(config, "metzoo.url", str)
        self.__validate_config_property_type(config, "opc", dict)
        self.__validate_config_property_type(config, "opc.gateway", str, optional=True)
        self.__validate_config_property_type(config, "opc.host_name", str, optional=True)
        self.__validate_config_property_type(config, "opc.server_name", str)
        self.__validate_config_property_type(config, "opc.mapping", dict)

        for key, value in config.get("opc.mapping").iteritems():
            self.__validate_type("opc.mapping.{}.value".format(key), value, dict)
            self.__validate_type("opc.mapping.{}.value.{}.value".format(key, "agent"), value["agent"], str)
            self.__validate_type("opc.mapping.{}.value.{}.value".format(key, "metric"), value["metric"], [str,unicode])

    def __validate_config_property_type(self, config, name, expected, optional=False):
        try:
            value = config.get(name)
        except:
            value = None

        if optional and value is None:
            return

        self.__validate_type("config.{}".format(name), value, expected, optional)

    def __validate_type(self, name, value, expected, optional=False):
        got = type(value)
        if not (got == expected or type(expected) == list and got in expected):
            raise TypeError("for '{}' got {} expected {}".format(name, got, expected))

    @property
    def _opc(self):
        if self.__opc is None:
            try:
                self.__opc = OpenOPC.open_client(self.__config.get("opc.gateway"))
            except KeyError:
                self.__opc = OpenOPC.client()

            host = self.__config.get("opc.host_name", None)
            server = self.__config.get("opc.server_name", None)

            if server is None:
                raise ValueError("opc.server_name if empty")

            connected = True
            try:
                if host is None:
                    self.__opc.connect(server)
                else:
                    self.__opc.connect(server, host)
            except OpenOPC.OPCError as e:
                connected = False

            if not connected:
                raise RuntimeError("can't connect to host: {}, server: {} ".format(host, server))

        return self.__opc
