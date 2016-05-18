# encoding: utf-8
from __future__ import absolute_import
import json
import logging

from sd.utils import protobuf_to_dict
from sd.strategy.bean import protoquote

__author__ = u'Yonka'


class BaseBean(object):
    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        def _get_v_from_type(t, v):
            v_to_dict = getattr(t, u"to_dict", None)
            if v_to_dict is None:
                return unicode(v)
            else:
                return t.to_dict(v)

        d = dict(self.__dict__)
        types = getattr(self.__class__, u"_types", None)
        if not types:
            return d
        for k, t in types.items():
            v = d.get(k)
            if v is None:
                continue
            if issubclass(t, list):
                params = getattr(t, u"__parameters__", None)
                if params is None:
                    continue
                v = [_get_v_from_type(params[0], vi) for vi in v]
            else:
                v = _get_v_from_type(t, v)
            d[k] = v
        return d

    def from_json(self, s):
        u"""use json content to fulfill current instance
        @:param s json str
        @:return current instance
        """
        d = json.loads(s)
        return self.from_dict(d)

    def from_dict(self, d):
        def _get_v_from_constructor(c, v):
            params = getattr(c, u"__parameters__", None)
            if params:
                if issubclass(c, list):
                    return [_get_v_from_constructor(params[0], vi) for vi in v]
            handler = None
            if hasattr(c, u"from_value"):
                handler = getattr(c, u"from_value")
            elif hasattr(c, u"from_dict"):
                handler = getattr(c, u"from_dict")
            if handler is None:
                return c(v)
            else:
                res = c()
                handler(res, v)
                return res

        if not d:
            return

        types = getattr(self.__class__, u"_types", None)
        for k, v in d.items():
            if k in self.__dict__:
                if types and k in types:
                    constructor = types[k]
                    v = _get_v_from_constructor(constructor, v)
                self.__dict__[k] = v  # enum呢？ 非基本类型呢？，自行指定类型信息
        return self


def proto_to_bean(s, proto_t, bean_t):
    proto_t_obj = proto_t()
    proto_t_obj.ParseFromString(s)
    return bean_t().from_dict(protobuf_to_dict.protobuf_to_dict(proto_t_obj))


def json_load_bean_list(s, t, l=None):
    """
    @:param t type, should be subclass of BaseBean
    """
    j = json.loads(s)
    if j is None:
        return None
    elif not isinstance(j, list):
        logging.error("s: (%s) is not list", s)
        raise ValueError("not list")
    if l is None:
        l = []
    for ji in j:
        l.append(t().from_dict(ji))
    return l


def history_data_proto_2_bean_list(s, proto_t, t, l=None):
    """
    @:param t type, should be subclass of BaseBean
    """
    j = protoquote.HistoryDataBean()
    j.ParseFromString(s)
    if l is None:
        l = []
    for ji in j.historyData:
        l.append(proto_to_bean(ji, proto_t, t))
    return l
