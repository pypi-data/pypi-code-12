from flask import (request)
from ..api.fields import (List, Nested)
from ..api.errors import ZeusNotFound


class QueryMixin(object):
    # 模型
    model = None
    # 排序
    order_by = None

    # 页码
    # type: int
    page = 1

    # 每页数据个数
    # type: int
    per_page = 20

    can_empty = None

    def get_paginate_args(self):
        """ 获取分页参数 """
        page = request.args.get('page', self.page, type=int) or self.page
        per_page = request.args.get('per_page', self.per_page, type=int) or self.per_page
        return page, per_page

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

    def merge_data(self, items):
        pass

    def get_item(self, **kwargs):
        stmt = self.get_query(**kwargs)
        item = stmt.first()
        if not item:
            raise ZeusNotFound
        return item

    def get_pagination(self, **kwargs):
        stmt = self.get_query(**kwargs)
        page, per_page = self.get_paginate_args()
        pagination = stmt.paginate(page, per_page, error_out=not self.can_empty)
        self.merge_data(pagination.items)
        return pagination

    def get_items(self, **kwargs):
        stmt = self.get_query(**kwargs)
        return stmt.all()


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


class FormMixin(object):
    # 是否开始csrf验证
    # type: bool
    csrf_enabled = False

    # 创建数据使用的表单
    # type: wtforms obj
    create_form = None

    # 更新数据使用的表单
    # type: wtforms obj
    update_form = None

    # 删除数据使用的表单
    # type: wtforms obj
    delete_form = None

    def get_form(self, form_cls, obj=None, **kwargs):
        form = form_cls(obj=obj, csrf_enabled=self.csrf_enabled)
        for k, v in kwargs.items():
            if form.has_field(k):
                getattr(form, k).data = v
        return form

    def get_create_form(self, **kwargs):
        if not self.create_form:
            raise AttributeError('需要设置create_form')
        return self.get_form(self.create_form, **kwargs)

    def get_update_form(self, **kwargs):
        if not self.update_form:
            raise AttributeError('需要设置update_form')
        return self.get_form(self.update_form, **kwargs)

    def get_delete_form(self, **kwargs):
        if self.delete_form:
            return self.get_form(self.delete_form, **kwargs)