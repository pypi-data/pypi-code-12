# encoding=utf-8
"""
功能:
作者:
创建时间:
"""
import redis
import uuid
import exceptions


REDIS_CONNECT_SET = {
    "host":"localhost",
    "port":6379,
    "db":0,
    "password":None,
}


def _conver_match_value(connect, value):
    # 由于在redis设置value的时候 会出现一些转码 这些转码会导致使用 sscan进行match的
    # 时候不能匹配成功 所以每次先使用redis返回一个我们match的值
    # 比如 objects--a__id=* 我们要先通过redis获取一下值 他会转变成
    # objectstitle\xe2\x80\x94\xe2\x80\x94aa__id=* 这种格式 如果不转换 就match不到了
    redis_key = uuid.uuid1()
    cursor = connect.pipeline()
    ret = cursor.set(redis_key, value).get(redis_key).execute()[1]
    cursor.delete(redis_key).execute()
    return ret


def _AND(connect, *args, **kwargs):
    """
    构造多个条件与的方法 方式类似于
    _AND(name="cxxxx", age=20, )
    返回的内容应该是
    [{field:"name", condition: "cxxxx__id=*"},
     {field:"age", condition: "20__id=*"}
    ]
    """
    keys = kwargs.keys()
    result =[]
    for key in keys:
        # result.append(dict(field=key,
        #                    condition="%s__id=*" % _conver_match_value(connect, kwargs[key])))
        # TODO::好像在redis的2.8这个版本中 只要都是utf-8的 可以全部匹配
        # TODO::不需要再连接一下redis返回的值 此处还需要再进行测试
        result.append(dict(field=key,
                           condition="%s__id=*" % kwargs[key]))
    return result


class ModelManager(object):
    """
    一个模型管理的类 每一个model的类
    默认会拥有一个这样的实例 用于进行
    模型的创建 查找等操作
    """

    def __init__(self, cls):
        self.model_cls = cls
        self._redis = None
        # 获取模型的所有字段名
        self.fields_name = getattr(self.model_cls, "__fields_name")

    @property
    def redis(self):
        self._redis = self._redis if self._redis else \
            redis.StrictRedis(REDIS_CONNECT_SET["host"], REDIS_CONNECT_SET["port"],
                              REDIS_CONNECT_SET["db"], REDIS_CONNECT_SET["password"])
        return self._redis

    def _get_cur_max_id(self, id=None):
        # 每一个表会有一个单独的键 用于保存当前的最大id
        # 键名为 app.table_name.having.insert.max.id
        from redisOrm import RedisModel
        key_name = "%s.%s.having.insert.max.id" % (getattr(self.model_cls.Meta, "app_name", RedisModel.Meta.app_name),
                                         getattr(self.model_cls.Meta, "table_name",
                                                 self.model_cls.__name__))
        max_id = self.redis.get(key_name)
        return long(max_id) if max_id else 0

    def _set_cur_max_id(self, id):
        from redisOrm import RedisModel
        key_name = "%s.%s.having.insert.max.id" % (getattr(self.model_cls.Meta, "app_name", RedisModel.Meta.app_name),
                                 getattr(self.model_cls.Meta, "table_name",
                                         self.model_cls.__name__))
        _id =self.redis.get(key_name) if self.redis.get(key_name) else 0
        max_id = max(long(_id), long(id))
        return self.redis.pipeline().set(key_name, long(max_id)).execute()

    def _auth_args_in_fields(self, keys):
        """
        验证所传递的参数是当前模型的所有字段名
        """
        for key in keys:
            if key not in self.fields_name:
                raise AttributeError("%s has no the %s attribute" % self.model_cls.__name__, key)

    def create(self, *args, **kwargs):
        """
        创建一个模型实例 并在redis数据库中插入这条记录
        """
        from redisOrm import RedisModel
        # 验证所给的参数 是否在模型中定义
        self._auth_args_in_fields(kwargs.keys())
        # 创建类的实例化对象
        model = self.model_cls()

        # 转换所有字段的为实际值 而不再是一个Field对象
        for attr in self.fields_name:
            if attr == "id": # id属性单独设置
                continue
            attr_obj = getattr(self.model_cls, attr)
            # 检查这个字段是否是必须的
            if attr_obj.is_must:
                if attr not in kwargs.keys():
                    raise ValueError("%s is a must attrbute" % attr)

                setattr(model, attr, attr_obj.convert_to_db(kwargs.get(attr, attr_obj.default)))
            else:
                setattr(model, attr, attr_obj.convert_to_db(kwargs.get(attr, attr_obj.default)))

        # 看是否直接指明ID的值 如果没有指明需要给它redis中还没有的值 否则以这个值为准
        if "id" not in kwargs.keys():
            # 如果没有直接指明id 那么id必须设置为自动递增 否则报错
            if not model.id.auto_incr:
                raise AttributeError("id must be indicated, because the id is not setted auto_incr")
            setattr(model, "id", self._get_cur_max_id()+1)
        # 新的键名
        key_name = "%s.%s.%s" % (getattr(self.model_cls.Meta, "app_name", RedisModel.Meta.app_name),
                                 getattr(self.model_cls.Meta, "table_name", self.model_cls.__name__),
                                 model.id)

        cursor = self.redis.pipeline()
        # 对该键的所有字段赋值
        for attr in self.fields_name:
            if attr == "id":
                continue # id字段 就不要加后缀了
            cursor.hset(key_name, attr, getattr(model, attr))
            # 新的字段名称 app.table_name.fields.field_name
            field_name = "%s.%s.fields.%s" % (getattr(self.model_cls.Meta, "app_name", RedisModel.Meta.app_name),
                                              getattr(self.model_cls.Meta, "table_name",self.model_cls.__name__),
                                              attr)
            # 所有字段后缀均加上属于哪一个id attr__id=xxx
            cursor.sadd(field_name, "%s__id=%s" % (getattr(model, attr), model.id))
        # 单独设置id字段
        field_name = "%s.%s.fields.%s" % (getattr(self.model_cls.Meta, "app_name", RedisModel.Meta.app_name),
                                                  getattr(self.model_cls.Meta, "table_name",self.model_cls.__name__),
                                                  "id")
        cursor.sadd(field_name, model.id)
        cursor.hset(key_name, "id", model.id)
        cursor.execute()
        self._set_cur_max_id(model.id)
        return model

    def filter(self, *args, **kwargs):
        """
        根据条件进行查找 返回多个模型实例的列表
        """
        def _process_match(it):
            # 取出匹配的字符串 然后只需要id的值即可 返回一个集合
            return {v[v.rfind("__id")+5:] for v in it}

        # 先实现交集操作 a=b&c=d&e=f这种
        # 所有的参数 应该在这个字段中
        # 验证所有的过滤的参数在这个字段中
        self._auth_args_in_fields(kwargs.keys())

        # 转换需要过滤的参数
        params = _AND(self.redis, *args, **kwargs)

        # 开始匹配所有的参数 使用redis的sscan这个命令进行匹配
        all_match_ids = []
        for param in params:
            # 构建储存在redis中的字段名字
            redis_field_name = "%s.%s.fields.%s" % (self.model_cls.Meta.app_name,
                                 getattr(self.model_cls.Meta, "table_name", self.model_cls.__name__),
                                 param["field"])
            result = self.redis.sscan_iter(redis_field_name, param["condition"])
            ids = _process_match(result)
            all_match_ids.append(ids)
        # 求出所有id的交集 如果没有匹配则引发一个异常

        if not all_match_ids:
            raise exceptions.BaseException.__new__(self.model_cls.DoesNotExits)

        ids = all_match_ids[0]
        for set_id in all_match_ids:
            ids = ids&set_id
        # 根据获取到的id来创建模型对象
        for id in ids:
            record = self.get_by_id(id)
            yield record

    def get(self, *args, **kwargs):
        """
        返回一个实例, 如果没有匹配到引发一个DoesNotExits
        """
        generator = self.filter(*args, **kwargs)
        try:
            ret = generator.next()
        except StopIteration:
            raise exceptions.BaseException.__new__(self.model_cls.DoesNotExits)
        finally:
            del generator
        return ret

    def get_by_id(self, id):
        # 根据id获得键名
        key_name = "%s.%s.%s" % (self.model_cls.Meta.app_name,
                                 getattr(self.model_cls.Meta, "table_name", self.model_cls.__name__),
                                 id)
        result = self.redis.hgetall(key_name)
        if not result:
            return None

        model = self.model_cls()

        fields_name = getattr(self.model_cls, "__fields_name")
        for field in fields_name:
            field_attr = getattr(self.model_cls, field)
            setattr(model, field, field_attr.convert_to_db(result[field]))

        return model