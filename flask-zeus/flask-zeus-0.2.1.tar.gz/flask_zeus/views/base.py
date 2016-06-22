from flask import (request, url_for, render_template)
from flask.views import View
from .._common.mixin import QueryMixin, ContextMixin
import types


class BaseView(View, QueryMixin, ContextMixin):
    # 模版
    template = None

    def get_template(self):
        """ 获取模版 """
        if not self.template:
            raise AttributeError('需要设置template值')
        return self.template

    def before_render(self):
        pass

    def after_render(self):
        pass

    def render(self, template=None, context=None):
        """ 渲染模版 """
        template = template or self.get_template()

        if context and isinstance(context, types.MappingProxyType):
            for k, v in context.items():
                self.append_context(k, v)

        self.before_render()
        response = render_template(template, **self.context)
        self.after_render()
        return response

    def get_next_url(self, **kwargs):
        """ 获取跳转链接 """
        return request.args.get('next') or url_for(request.endpoint, **kwargs)

