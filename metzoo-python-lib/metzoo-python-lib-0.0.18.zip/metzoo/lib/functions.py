# -*- coding: utf-8 -*-

from .utils import sanitize


class MetricFunction(object):
    def __init__(self, metric, function, inputs, unit=None, schedule=None, params=None):
        self.metric = sanitize(metric, "metric", [str, unicode])
        self.function = sanitize(function, "function", [str, unicode])
        self.inputs = sanitize(inputs, "inputs", list)
        self.inputs = map(lambda x : sanitize(x[1], "input {}".format(x[0]), MetricInput), enumerate(self.inputs))
        self.unit = sanitize(unit, "unit", [type(None), str, unicode])
        self.schedule = sanitize(schedule, "schedule", [type(None), str, unicode])
        self.params = sanitize(params, "params", [type(None), dict])

    def as_dict(self):
        d = { "name": self.metric
            , "function": self.function
            , "input": map(lambda i : i.as_dict(), self.inputs)
            }

        if self.unit is not None:
            d["unit"] = self.unit

        if self.schedule is not None:
            d["schedule"] = self.schedule

        if self.params is not None:
            d["parameters"] = self.params

        return d


class MetricInput(object):
    def __init__(self, name, agent):
        self.name = sanitize(name, "name", str)
        self.agent = sanitize(agent, "agent", str)

    def as_dict(self):
        return {"name": self.name, "agent": self.agent}
