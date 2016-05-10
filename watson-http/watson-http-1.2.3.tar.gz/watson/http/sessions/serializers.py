# -*- coding: utf-8 -*-
import abc
import json


class Base(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def encode(self, value):
        raise NotImplementedError('encode must be implemented')

    @abc.abstractmethod
    def decode(self, value):
        raise NotImplementedError('decode must be implemented')


class Json(Base):
    def encode(self, value, **kwargs):
        return json.dumps(value, **kwargs)

    def decode(self, value, **kwargs):
        return json.loads(value, **kwargs)
