from flask import request
from .base import BaseView


class BaseListView(BaseView):
    per_page = 20
    error_out = False

    def get_paginate_args(self):
        """ 获取分页参数 """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', self.per_page, type=int)
        return page, per_page


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