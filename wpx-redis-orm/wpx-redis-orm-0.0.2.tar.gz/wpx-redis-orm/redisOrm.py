# encoding=utf-8
"""
功能:基于redis的ORM模型的编写
作者:wupeaking
创建时间:2016-5-1 15:25:37
"""
from manager import ModelManager

class DoesNotExitsExpection(BaseException):

    def __str__(self):
        return "no extis this records..."

class AbstractField(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "")
        self.is_must = kwargs.get("is_must", False)

class CharField(AbstractField):
    _MAX_LENGTH = 128

    def __init__(self, *args, **kwargs):
        super(CharField, self).__init__(args, kwargs)
        self.default = kwargs.get("default", "")
        self.max_length = kwargs.get("max_length", CharField._MAX_LENGTH)

    def convert_to_db(self, v):
        value = str(v)
        if len(value) > self.max_length:
            raise ValueError("CharField  max length is setted %s" % self.max_length)
        else:
            return value


class IntField(AbstractField):
    def __init__(self, *args, **kwargs):
        super(IntField, self).__init__(args, kwargs)
        self.default = kwargs.get("default", 0)

    def convert_to_db(self, v):
        value = int(v)
        if value < -2147483648 or value > 2147483647:
            raise ValueError("IntField is 32bit -2147483648 ~ 2147483647")
        else:
            return value


class LongField(AbstractField):
    def __init__(self, *args, **kwargs):
        super(LongField, self).__init__(args, kwargs)
        self.default = kwargs.get("default", 0)

    def convert_to_db(self, v):
        value = long(v)
        if value < -9223372036854775808 or value > 9223372036854775807:
            raise ValueError("longField is 64bit -9223372036854775808 ~ 9223372036854775807")
        else:
            return value


class PrimaryKeyField(LongField):
    def __init__(self, *args, **kwargs):
        self.auto_incr = kwargs.get("auto", True)
        super(PrimaryKeyField, self).__init__(args, kwargs)

def _get_field_attr(cls):
    field_attr_obj = []
    field_attr_name = []
    for attr in dir(cls):
        attr_obj = getattr(cls, attr)
        if isinstance(attr_obj, AbstractField):
            field_attr_obj.append(attr_obj)
            field_attr_name.append(attr)
    return field_attr_name, field_attr_obj

class RedisModelBase(type):
    def __init__(cls, name, base, attr):
        super(RedisModelBase, cls).__init__(name, base, attr)
        __fields_name, __fields_obj = _get_field_attr(cls)
        setattr(cls, "__fields_obj", __fields_obj)
        setattr(cls, "__fields_name", __fields_name)
        object = ModelManager(cls)
        setattr(cls, "objects", object)


class RedisModel(object):
    """
    一个redis模型的基类 每次创建的表模型 都应该继承这个类的属性
    """
    __metaclass__ = RedisModelBase

    # 记录不存在的异常类型
    DoesNotExits = DoesNotExitsExpection

    @classmethod
    def managers(cls):
        return ModelManager(cls)

    # 应该具有的一些私有属性
    class Meta:
        app_name = "redis_orm"
        abstract = False

    # 默认具有一个id
    id = PrimaryKeyField(auto=True)


