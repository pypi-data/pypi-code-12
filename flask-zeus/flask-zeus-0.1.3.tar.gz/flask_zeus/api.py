from flask import (request, url_for)
from flask_zeus.fields import (List, Nested)


class BaseResource(object):
    # 模型
    # type: sqlalchemy obj 需要继承 CRUDMixin
    model = None
    model_fields = None
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

    def check_model(self):
        """ 检查模型是否设置
        :return:
        """
        assert self.model, 'API Class: {} model not set'.format(self.cls_name)

    def check_create_form(self):
        """ 检查创建表单是否设置
        :return:
        """
        assert self.create_form, 'API Class: {} create_form not set'.format(self.cls_name)

    def check_update_form(self):
        """ 检查更新表单是否设置
        :return:
        """
        assert self.update_form, 'API Class: {} update_form not set'.format(self.cls_name)

    def check_model_fields(self):
        """ 检查输出格式是否设置
        :return:
        """
        assert self.model_fields, 'API Class: {} model_fields not set'.format(self.cls_name)

    def get_stmt(self, **kwargs):
        """ 自定义stmt语句, 需重写, 提供给get方法使用
        :return: sqlalchemy query
        """
        return None

    def generate_stmt(self, **kwargs):
        """ 生成查询语句
        :param kwargs:
        :return: sqlalchemy query
        """
        # 如有自定义语句,直接返回
        if self.get_stmt(**kwargs):
            return self.get_stmt(**kwargs)

        stmt = self.model.query

        # 处理url主体,?之前
        filter_by_ = {}

        for k, v in kwargs.items():
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

        # 处理自定义排序
        if self.order_by and isinstance(self.order_by, (list, tuple)):
            stmt = stmt.order_by(*self.order_by)

        if self.model.has_property('deleted'):
            stmt = stmt.filter_by(deleted=False)

        return stmt

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

    def format_return(self, fields):

        data = {}
        for name, field in fields.items():
            if isinstance(field, List):
                try:
                    data[name] = [self.format_return(field.container.nested)]
                except:
                    data[name] = [getattr(field.container, 'prompt', '')]
            elif isinstance(field, Nested):
                data[name] = self.format_return(field.nested)
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


from werkzeug.exceptions import *
from flask_restful import HTTPException
from collections import OrderedDict


class ZeusHTTPException(HTTPException):
    """
    code http状态码
    description 错误描述
    """

    def __init__(self, description=None, response=None, error_code=0, details=None):
        """
        :param description: 自定义错误描述
        :param response: 自定义响应数据
        :param error_code: 自定义错误代码
        :param details: 自定义错误详情
        :return:
        """
        self.status_code = self.code
        self.message = description or self.description
        self.error_code = error_code
        self.details = details or {}
        super(ZeusHTTPException, self).__init__(description, response)

    def as_dict(self):
        """
        :return: {
            'status_code': ...,
            'error_code': ...,
            'message': ...,
            'details': ...
        }
        """
        data = OrderedDict()
        for k in ['status_code', 'error_code', 'message', 'details']:
            data[k] = getattr(self, k)
        return data

    @property
    def data(self):
        return self.as_dict()


class ZeusBadRequest(BadRequest, ZeusHTTPException):
    """ 400
    """
    pass


class ZeusUnauthorized(Unauthorized, ZeusHTTPException):
    """ 401
    """
    pass


class ZeusNotFound(NotFound, ZeusHTTPException):
    """ 404
    """
    pass


class ZeusMethodNotAllowed(MethodNotAllowed, ZeusHTTPException):
    """ 405
    """
    pass

from flask import request
from flask_restful import (Resource, marshal)
from flask_login import (login_required, current_user)
from collections import ChainMap


class RestfulResource(BaseResource, Resource):
    """
    example:
        from app.models import Post
        from app.forms import PostCreateForm, PostUpdateForm
        from app.model_fields import post_fields

        @api.resource('/posts/', '/posts/<int:id>/')
        class PostAPI(ModelResource):
            model = Post
            create_form = PostCreateForm
            update_form = PostUpdateForm
            model_fields = post_fields
            can_create = True
            can_update = True
            can_delete = True
    """

    def get(self, **kwargs):
        """ 资源获取
        :param kwargs:
        :return: dict
        """
        if not self.can_read:
            raise ZeusMethodNotAllowed

        self.check_model()
        self.check_model_fields()

        stmt = self.generate_stmt(**kwargs)

        if kwargs.get('id'):
            item = stmt.first()
            if not item:
                raise ZeusNotFound
            return marshal(item, self.model_fields)

        if self.can_paginate:
            page = request.args.get('page', self.default_page, int) or self.default_page
            per_page = request.args.get('per_page', self.default_per_page, int) or self.default_per_page
            pagination = stmt.paginate(page, per_page, error_out=not self.can_empty)
            items = self.merge_data(pagination.items)
            return {
                'items': marshal(items, self.model_fields),
                'pagination': OrderedDict([
                    ('has_prev', pagination.has_next),
                    ('has_next', pagination.has_next),
                    ('prev_num', pagination.prev_num),
                    ('next_num', pagination.next_num),
                    ('prev_url', self.generate_url(pagination.prev_num, per_page, **kwargs) if pagination.has_prev else ''),
                    ('next_url', self.generate_url(pagination.next_num, per_page, **kwargs) if pagination.has_next else ''),
                    ('page', pagination.page),
                    ('per_page', per_page),
                    ('pages', pagination.pages),
                    ('total', pagination.total),
                    ('iter_pages', self.generate_iter_pages(pagination.iter_pages(), per_page, **kwargs)),
                ])
            }
        else:
            items = stmt.all()

            if not self.can_empty and not items:
                raise ZeusNotFound

            return marshal(items, self.model_fields)

    @login_required
    def post(self, **kwargs):
        """ 资源创建
        :param kwargs:
        :return: dict
        """
        if not self.can_create:
            raise ZeusMethodNotAllowed

        self.check_model()
        self.check_create_form()
        self.check_model_fields()

        if not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        form = self.create_form(csrf_enabled=self.csrf_enabled)

        for k, v in kwargs.items():
            field = getattr(form, k, None)
            if field:
                field.data = v

        if form.validate_on_submit():
            data = ChainMap(form.data, kwargs)
            item = self.model()

            for k, v in data.items():
                setattr(item, k, v)

            if self.model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()
            return marshal(item, self.model_fields), 201

        raise ZeusBadRequest(details=form.errors)

    @login_required
    def put(self, **kwargs):
        """ 资源更新
        :param kwargs:
        :return: dict
        """
        if not self.can_update:
            raise ZeusMethodNotAllowed

        self.check_model()
        self.check_update_form()
        self.check_model_fields()

        if not kwargs or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            raise ZeusNotFound

        if item.user_id != current_user.id:
            raise ZeusUnauthorized

        form = self.update_form(csrf_enabled=self.csrf_enabled)

        for k, v in kwargs.items():
            field = getattr(form, k)
            if field:
                field.data = v

        if form.validate_on_submit():
            for k, v in form.data.items():
                setattr(item, k, v)
            item.save()
            return marshal(item, self.model_fields), 200

        raise ZeusBadRequest(details=form.errors)

    @login_required
    def delete(self, **kwargs):
        """ 资源删除
        :param kwargs:
        :return: None
        """
        if not self.can_delete:
            raise ZeusMethodNotAllowed

        self.check_model()

        if not kwargs or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        if self.delete_form:
            form = self.delete_form()
            if not form.validate_on_submit():
                raise ZeusBadRequest(details=form.errors)

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            raise ZeusNotFound

        if item.user_id != current_user.id:
            raise ZeusUnauthorized

        item.delete()

        return {}, 204

    def options(self, **kwargs):
        allow = []
        data = {}

        if self.can_read:
            allow.append('GET')

            if self.url_parse:
                data['GET'] = {'args': self.output_args(self.url_parse)}

        if self.can_create:
            allow.append('POST')
            data['POST'] = self.create_form.fields(**kwargs)

        if self.can_update:
            allow.append('PUT')
            data['PUT'] = self.update_form.fields(**kwargs)

        if self.can_delete:
            allow.append('DELETE')

        if self.model_fields:
            data['return'] = self.format_return(self.model_fields)

        headers = {
            'Allow': ', '.join(allow),
        }
        return data, headers


from flask_restful import (Resource, marshal)
from flask_login import (login_required, current_user)


class ToggleResource(BaseResource, Resource):

    @login_required
    def post(self, **kwargs):
        self.check_model()
        self.check_model_fields()

        if not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            item = self.model()
            for k, v in kwargs.items():
                if self.model.has_property(k):
                    setattr(item, k, v)
            item.user_id = current_user.id
            item.save()
            return marshal(item, self.model_fields), 201

        item.delete()
        return {}, 204
