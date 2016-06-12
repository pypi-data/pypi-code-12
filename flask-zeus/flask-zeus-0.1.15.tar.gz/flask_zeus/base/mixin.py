from flask import request
from ..api.fields import (List, Nested)


class QueryMixin(object):
    # 模型
    model = None
    # 分页
    per_page = 20
    # 排序
    order_by = None

    def get_model(self):
        """ 获取模型 """
        if not self.model:
            raise AttributeError('需要设置model值')
        return self.model

    def get_stmt(self):
        """ 自定义查询语句 """
        return None

    def get_query_filter(self):
        """ 自定义查询条件 """
        return {}

    def get_query(self, **kwargs):
        """ 获取查询语句 """
        if self.get_stmt():
            return self.get_stmt()

        model = self.get_model()

        stmt = model.query

        # 处理url主体,?之前
        filter_by_ = {}

        kwargs.update(self.get_query_filter())

        for k, v in kwargs.items():
            if self.model.has_property(k):
                filter_by_[k] = v

        if filter_by_:
            stmt = stmt.filter_by(**filter_by_)

        # 处理url参数?之后
        # 默认参数为多值,使用in操作符
        # 如果参数为单值,并且开头或结尾为%,使用like操作符
        filter_ = []

        for k, v in request.args.lists():
            if self.model.has_property(k):
                if len(v) == 1 and (v[0].startswith('%') or v[0].endswith('%')):
                    filter_.append(getattr(self.model, k).ilike(v[0]))
                else:
                    filter_.append(getattr(self.model, k).in_(v))

        if filter_:
            stmt = stmt.filter(*filter_)

        if self.model.has_property('deleted'):
            stmt = stmt.filter_by(deleted=False)

        # 处理自定义排序
        if self.order_by and isinstance(self.order_by, (list, tuple)):
            stmt = stmt.order_by(*self.order_by)

        return stmt


class OutputMixin(object):

    def output_fields(self, fields):
        data = {}
        for name, field in fields.items():
            if isinstance(field, List):
                try:
                    data[name] = [self.output_fields(field.container.nested)]
                except:
                    data[name] = [getattr(field.container, 'prompt', '')]
            elif isinstance(field, Nested):
                data[name] = self.output_fields(field.nested)
            else:
                data[name] = getattr(field, 'prompt', '')

        return data

    def output_args(self, url_parse):
        args = []
        for item in url_parse.args:
            item_data = dict()
            item_data['name'] = item.name
            item_data['help'] = item.help
            item_data['type'] = item.type.__name__
            item_data['required'] = item.required

            if item.choices:
                item_data['choices'] = item.choices

            if item.default:
                item_data['default'] = item.default

            args.append(item_data)
        return args


class ContextMixin(object):
    __context = None

    @property
    def context(self):
        if not self.__context:
            self.__context = dict()
        return self.__context

    def append_context(self, k, v):
        self.context[k] = v

    def remove_context(self, k):
        if k in self.context.keys():
            del self.context[k]