# -*- coding: utf-8 -*-

from .fields import BaseField
from .vals import default_app


class Model(object):

    # 默认
    __jsonm_app__ = default_app

    def __init__(self):
        for attr, field_def in self._fields_dict().items():
            setattr(self, attr, field_def.get_default())

    def to_json(self):
        """
        导出为json
        从外层到内层
        :return:
        """
        self.validate()

        value = dict()
        for attr in self._fields_dict().keys():
            value[attr] = getattr(self, attr, None)

        json_object = dict(
            __class__=self.__class__.__name__,
            __value__=value
        )

        self.on_to_json_over(json_object)

        return json_object

    def from_json(self, json_object):
        """
        从json解析
        从内层到外层
        :param json_object:
        :return:
        """

        json_value = json_object['__value__']

        for attr in self._fields_dict().keys():
            # 如果json里面没有这个attr，就应该保持目前的数据不变
            if attr in json_value:
                setattr(self, attr, json_value.get(attr))

        self.on_from_json_over()

    def on_to_json_over(self, json_object):
        """
        导出为json之后的处理
        :param json_object: 导出的json数据
        :return:
        """
        pass

    def on_from_json_over(self):
        """
        从json解析后的处理
        :return:
        """
        pass

    def _fields_dict(self):
        """
        获取fields
        :return:
        """

        fields_dict = dict()

        for attr in dir(self.__class__):
            val = getattr(self.__class__, attr)
            if isinstance(val, BaseField):
                fields_dict[attr] = val

        return fields_dict

    def validate(self):
        """
        验证参数是否合法
        :return:
        """

        for attr, field_def in self._fields_dict().items():
            try:
                field_def.validate(getattr(self, attr, None))
            except Exception, e:
                raise ValueError('%s.%s validate fail. %s' % (self.__class__.__name__, attr, e.message))

    def __repr__(self):
        return self.__jsonm_app__.json_dumps(self, indent=4)
