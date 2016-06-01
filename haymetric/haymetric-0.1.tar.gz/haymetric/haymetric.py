# -*- coding: utf-8 -*-

"""
Haymetric Python Library
Copyright © 2016 Haymetric.com. All rights reserved.
"""

import os
import stat
import time
import datetime
import subprocess

TIMESTAMP_LINE = "Timestamp=%d\n"
METRICS_LINE = "Metrics="
DIMENSIONS_LINE = "Dimensions="
DATA = "data"
UNIT = "unit"

def execute(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = p.wait()
    return type('ExecuteResult', (), \
        {"return_code": ret, \
        "stdout": p.stdout.readlines(), \
        "stderr": p.stderr.readlines()})

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def key_value_dict_to_str(kv_dict):
    result = ""
    i = 0
    num_keys = len(kv_dict)
    for key in sorted(kv_dict):
        i += 1
        result += key + "=" + str(kv_dict[key])
        if i < num_keys:
            result += ","
    return result

Units = enum("NONE", "NANOSECOND", "MICROSECOND", "MILLISECOND", "SECOND", \
    "MINUTE", "HOUR", "BYTE", "KILOBYTE", "MEGABYTE", "GIGABYTE")

Rotations = enum("MINUTELY", "HOURLY", "DAILY")

class Scope:
    def __init__(self):
        self.counters = {}
        self.values = {}

    def add_counter(self, counter, value):
        if counter in self.counters:
            self.counters[counter] += value
        else:
            self.counters[counter] = value

    def add_value(self, value_name, value, unit=Units.NONE):
        if value_name in self.values:
            self.values[value_name][DATA].append(value)
            self.values[value_name][UNIT] = unit
        else:
            self.values[value_name] = {DATA: [value], UNIT: unit}

    def get_metrics(self):
        metrics = [self.__get_counters(), self.__get_values()]
        return METRICS_LINE + ",".join([m for m in metrics if m])

    def __get_counters(self):
        return key_value_dict_to_str(self.counters)

    def __get_values(self):
        metrics = ""
        i = 0
        num_values = len(self.values)
        for value in self.values:
            i += 1
            metrics += value + "=" + \
                "+".join(str(val) for val in self.values[value][DATA]) + \
                self.__get_unit(self.values[value][UNIT])
            if i < num_values:
                metrics += ","
        return metrics

    def __get_unit(self, unit):
        if unit is Units.NANOSECOND:
            return "ns"
        if unit is Units.MICROSECOND:
            return "us"
        if unit is Units.MILLISECOND:
            return "ms"
        if unit is Units.SECOND:
            return "s"
        if unit is Units.MINUTE:
            return "m"
        if unit is Units.HOUR:
            return "h"
        if unit is Units.BYTE:
            return "b"
        if unit is Units.KILOBYTE:
            return "kb"
        if unit is Units.MEGABYTE:
            return "mb"
        if unit is Units.GIGABYTE:
            return "gb"
        return ""


class Metric:
    def __init__(self, path, dimensions, rotation=Rotations.HOURLY):
        self.dimensions = self.__resolve_dimensions(dimensions)
        self.rotation = self.__get_rotation(rotation)
        self.path = path
        self.current_path = ""
        self.logfile = None
        self.scopes = {}

    def get_scope(self, scope_str=""):
        scope = key_value_dict_to_str(self.__resolve_dimensions(scope_str))
        if scope not in self.scopes:
            self.scopes[scope] = Scope()
        return self.scopes[scope]

    def flush(self, timestamp=None):
        if not timestamp:
            timestamp = int(time.time())
        logfile = self.__get_logfile(timestamp)
        for scope in self.scopes:
            dimensions = self.dimensions.copy()
            dimensions.update(self.__resolve_dimensions(scope))
            logfile.write(TIMESTAMP_LINE % timestamp)
            logfile.write(DIMENSIONS_LINE + key_value_dict_to_str(dimensions) + "\n")
            logfile.write(self.scopes[scope].get_metrics() + "\n---------\n")
        self.scopes.clear()

    def close(self):
        if self.logfile:
            self.logfile.close()
        self.current_path = ""
        self.logfile = None

    def __setup_folder(self):
        dirname = os.path.dirname(self.current_path)
        if not dirname:
            dirname = "."
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        # adjust permission to allow agent to cleanup old log files
        dir_stat = os.stat(dirname)
        if not (dir_stat.st_mode & stat.S_IWOTH):
            os.chmod(dirname, dir_stat.st_mode | stat.S_IWOTH)

    def __get_logfile(self, timestamp):
        current_path = self.__get_current_path(timestamp)
        if current_path is not self.current_path:
            self.close()
            self.current_path = current_path
            self.__setup_folder()
            self.logfile = open(self.current_path, "a")
        return self.logfile

    def __resolve_dimensions(self, scope):
        result = {}
        dimensions = scope.strip().split(",")
        for d in dimensions:
            try:
                key, value = d.strip().split("=")
                result[key.strip().lower()] = value.strip()
            except:
                pass
        return result

    def __get_rotation(self, rotation):
        if rotation not in [Rotations.MINUTELY, Rotations.DAILY]:
            return Rotations.HOURLY
        return rotation

    def __get_current_path(self, timestamp):
        now = datetime.datetime.fromtimestamp(timestamp)
        current_path = self.path
        if self.rotation is Rotations.MINUTELY:
            return current_path + "." + now.strftime("%Y-%m-%d-%H-%M")
        if self.rotation is Rotations.HOURLY:
            return current_path + "." + now.strftime("%Y-%m-%d-%H")
        if self.rotation is Rotations.DAILY:
            return current_path + "." + now.strftime("%Y-%m-%d")