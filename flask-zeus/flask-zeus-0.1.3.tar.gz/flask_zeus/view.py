from flask import (request, render_template, url_for, redirect, flash)
from flask.views import View
from flask_login import (login_required, current_user)


class BaseView(View):
    model = None
    template = None
    per_page = 20
    order_by = None

    def get_model(self):
        """ 获取模型 """
        if not self.model:
            raise AttributeError('需要设置model值')
        return self.model

    def get_template(self):
        """ 获取模版 """
        if not self.template:
            raise AttributeError('需要设置template值')
        return self.template

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

        stmt = self.model.query

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

    def get_context(self):
        """ 获取自定义上下文 """
        return {}

    def merge_data(self, items):
        """ 数据合并 """
        return items

    def render(self, **context):
        """ 渲染模版 """
        return render_template(self.get_template(), **context)


class BaseListView(BaseView):
    per_page = 20
    error_out = False

    def get_paginate_args(self):
        """ 获取分页参数 """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', self.per_page, type=int)
        return page, per_page


class BaseDetailView(BaseView):
    pass


class BaseFormView(BaseView):
    form = None
    csrf_enabled = False
    success_message = None
    methods = ['GET', 'POST']
    decorators = [login_required]

    def get_form(self):
        """ 获取 wtforms 表单"""
        if not self.form:
            raise AttributeError('需要设置form值')

        return self.form

    def get_next_url(self, **kwargs):
        """ 获取跳转链接 """
        return request.args.get('next') or url_for(request.endpoint, **kwargs)


class ListView(BaseListView):

    def dispatch_request(self, **kwargs):
        stmt = self.get_query(**kwargs)
        pagination = stmt.paginate(*self.get_paginate_args(), error_out=self.error_out)
        context = self.get_context()
        items = self.merge_data(pagination.items)
        context.update({
            'items': items,
            'pagination': pagination
        })
        return self.render(**context)


class DetailView(BaseDetailView):

    def dispatch_request(self, **kwargs):
        stmt = self.get_query(**kwargs)
        item = stmt.first()
        context = self.get_context()
        context.update({
            'item': item
        })
        return self.render(**context)


class CreateView(BaseFormView):

    def dispatch_request(self, **kwargs):
        form = self.get_form()(csrf_enabled=self.csrf_enabled)

        if form.validate_on_submit():

            item = self.model()

            for k, v in form.data.iteritems():
                setattr(item, k, v)

            item = item.update(commit=False, **kwargs)

            if self.model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()

            if self.success_message:
                flash(self.success_message, category='success')

            return redirect(self.get_next_url(**kwargs))

        context = self.get_context()
        context.update({
            'form': form
        })
        return self.render(**context)


class UpdateView(BaseFormView):

    def dispatch_request(self, **kwargs):

        stmt = self.get_query(**kwargs)
        item = stmt.first_or_404()

        form = self.get_form()(obj=item, csrf_enabled=self.csrf_enabled)

        if form.validate_on_submit():

            for k, v in form.data.iteritems():
                setattr(item, k, v)

            item = item.update(commit=False, **kwargs)

            if self.model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()

            if self.success_message:
                flash(self.success_message, category='success')

            return redirect(self.get_next_url(**kwargs))

        context = self.get_context()
        context.update({
            'form': form
        })
        return self.render(**context)