from flask import (request, url_for)
from .errors import ZeusNotFound
from ..base.mixin import QueryMixin, OutputMixin


class BaseResource(QueryMixin, OutputMixin):
    # 输出
    model_fields = None

    # url参数解析
    url_parse = None

    # 创建数据使用的表单
    # type: wtforms obj
    create_form = None

    # 更新数据使用的表单
    # type: wtforms obj
    update_form = None

    # 删除数据使用的表单
    # type: wtforms obj
    delete_form = None

    can_read = True
    # 是否允许创建
    # type: bool
    can_create = False

    # 是否允许更新
    # type: bool
    can_update = False

    # 是否允许删除
    # type: bool
    can_delete = False

    # 是否允许返回空数据
    # type: bool
    can_empty = True

    # 是否显示分页
    # type: bool
    can_paginate = True

    # 页码
    # type: int
    default_page = 1

    # 每页数据个数
    # type: int
    default_per_page = 20

    # 是否生成包含域名的完整url
    # type: bool
    is_full_url = True

    # 自定义排序
    # type: list or tuple or set
    order_by = None

    # 是否开始csrf验证
    # type: bool
    csrf_enabled = True

    @property
    def cls_name(self):
        """ 视图类名称
        :return: str
        """
        return self.__class__.__name__

    def get_model_fields(self):
        """ 检查输出格式是否设置
        :return:
        """
        if not self.model_fields:
            raise AttributeError('{} 需要设置model_fields'.format(self.cls_name))
        return self.model_fields

    def generate_iter_pages(self, pages, per_page, **kwargs):
        """ 生成分页
        :param pages:
        :param per_page:
        :return: list
        """
        pages = list(pages)
        iter_pages = []

        for page in pages:
            if isinstance(page, int):
                iter_pages.append({
                    'page': page,
                    'url': self.generate_url(page, per_page, **kwargs)
                })
            else:
                iter_pages.append({
                    'page': '...',
                    'url': ''
                })

        return iter_pages

    def generate_url(self, page, per_page, **kwargs):
        """ 生成链接
        :param page:
        :param per_page:
        :return: str
        """
        return url_for(request.endpoint, page=page, per_page=per_page, _external=self.is_full_url, **kwargs)

    def merge_data(self, data):
        return data

    def get_form(self, form_cls, obj=None, **kwargs):
        form = form_cls(obj=obj, csrf_enabled=self.csrf_enabled)
        for k, v in kwargs.items():
            if form.has_field(k):
                getattr(form, k).data = v
        return form

    def get_create_form(self, **kwargs):
        if not self.create_form:
            raise AttributeError('{} 需要设置create_form'.format(self.cls_name))
        return self.get_form(self.create_form, **kwargs)

    def get_update_form(self, **kwargs):
        if not self.update_form:
            raise AttributeError('{} 需要设置update_form'.format(self.cls_name))
        return self.get_form(self.update_form, **kwargs)

    def get_delete_form(self, **kwargs):
        if self.delete_form:
            return self.get_form(self.delete_form, **kwargs)

    def get_item(self, **kwargs):
        stmt = self.get_query(**kwargs)
        item = stmt.first()
        if not item:
            raise ZeusNotFound
        return item

    def get_pagination(self, **kwargs):
        page = request.args.get('page', self.default_page, int) or self.default_page
        per_page = request.args.get('per_page', self.default_per_page, int) or self.default_per_page
        stmt = self.get_query(**kwargs)
        pagination = stmt.paginate(page, per_page, error_out=not self.can_empty)
        items = self.merge_data(pagination.items)
        return pagination

    def get_itmes(self, **kwargs):
        stmt = self.get_query(**kwargs)
        return stmt.all()
