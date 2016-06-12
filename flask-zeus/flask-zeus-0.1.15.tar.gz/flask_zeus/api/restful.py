from flask import request
from flask_restful import (Resource, marshal)
from flask_login import (login_required, current_user)
from .base import BaseResource
from .errors import *


class RestfulApi(BaseResource, Resource):
    """
    example:
        from app.models import Post
        from app.forms import PostCreateForm, PostUpdateForm
        from app.model_fields import post_fields

        @api.resource('/posts/', '/posts/<int:id>/')
        class PostAPI(RestfulApi):
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

        if kwargs.get('id'):
            item = self.get_item(**kwargs)
            return marshal(item, self.get_model_fields())

        if self.can_paginate:
            pagination = self.get_pagination(**kwargs)
            return {
                'items': marshal(pagination.items, self.get_model_fields()),
                'pagination': OrderedDict([
                    ('has_prev', pagination.has_next),
                    ('has_next', pagination.has_next),
                    ('prev_num', pagination.prev_num),
                    ('next_num', pagination.next_num),
                    ('prev_url', self.generate_url(pagination.prev_num, pagination.per_page, **kwargs) if pagination.has_prev else ''),
                    ('next_url', self.generate_url(pagination.next_num, pagination.per_page, **kwargs) if pagination.has_next else ''),
                    ('page', pagination.page),
                    ('per_page', pagination.per_page),
                    ('pages', pagination.pages),
                    ('total', pagination.total),
                    ('iter_pages', self.generate_iter_pages(pagination.iter_pages(), pagination.per_page, **kwargs)),
                ])
            }
        else:
            items = self.get_items(**kwargs)

            if not self.can_empty and not items:
                raise ZeusNotFound

            return marshal(items, self.get_model_fields())

    @login_required
    def post(self, **kwargs):
        """ 资源创建
        :param kwargs:
        :return: dict
        """
        if not self.can_create:
            raise ZeusMethodNotAllowed

        if not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        form = self.get_create_form(**kwargs)

        if form.validate_on_submit():
            model = self.get_model()
            item = model()

            for k, v in form.data.items():
                setattr(item, k, v)

            if model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()

            return marshal(item, self.get_model_fields()), 201

        raise ZeusBadRequest(details=form.errors)

    @login_required
    def put(self, **kwargs):
        """ 资源更新
        :param kwargs:
        :return: dict
        """
        if not self.can_update:
            raise ZeusMethodNotAllowed

        if not kwargs or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        item = self.get_item(**kwargs)

        if item.user_id != current_user.id:
            raise ZeusUnauthorized

        form = self.get_update_form(**kwargs)

        if form.validate_on_submit():
            for k, v in form.data.items():
                setattr(item, k, v)

            item.save()

            return marshal(item, self.get_model_fields()), 200

        raise ZeusBadRequest(details=form.errors)

    @login_required
    def delete(self, **kwargs):
        """ 资源删除
        :param kwargs:
        :return: None
        """
        if not self.can_delete:
            raise ZeusMethodNotAllowed

        if not kwargs or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        form = self.get_delete_form(**kwargs)

        if form and not form.validate():
            raise ZeusBadRequest(details=form.errors)

        item = self.get_item(**kwargs)

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

        if self.get_model_fields():
            data['return'] = self.output_fields(self.model_fields)

        headers = {
            'Allow': ', '.join(allow),
        }
        return data, headers