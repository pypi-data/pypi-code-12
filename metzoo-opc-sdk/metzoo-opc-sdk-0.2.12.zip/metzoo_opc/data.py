# -*- coding: utf-8 -*-

class OPCData(object):
    def __init__(self, data_id, tag, value, quality, timestamp, mapping):
        if type(value) is bool:
            value= int(value)
        self._data_id = data_id
        self._tag = tag
        self._value = value
        self._quality = quality
        self._timestamp = timestamp
        self._agent = mapping[tag]["agent"]
        self._metric = mapping[tag]["metric"]

    @property
    def data_id(self):
        return self._data_id

    @property
    def tag(self):
        return self._tag

    @property
    def value(self):
        return self._value

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def quality(self):
        return self._quality

    @property
    def agent(self):
        return self._agent

    @property
    def metric(self):
        return self._metric

    def __getitem__(self, key):
        if key == "timestamp":
            return self._timestamp
        elif key == "agent":
            return self._agent
        else:
            return None
    
    def __repr__(self):
        return "<OPCData id:{} tag:{} value:{} timestamp:{} quality:{}>".format(
                self.data_id, self.tag, self.value, self.timestamp, self.quality)
