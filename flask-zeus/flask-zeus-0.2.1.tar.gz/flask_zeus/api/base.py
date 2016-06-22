from flask import (request, url_for)
from .._common.mixin import (QueryMixin, OutputMixin, FormMixin)


class BaseResource(QueryMixin, OutputMixin, FormMixin):
    # 输出
    model_fields = None

    # url参数解析
    url_parse = None

    # 是否生成包含域名的完整url
    # type: bool
    is_full_url = True

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


class Item(object):

    def __init__(self, data=None):
        self.data = data or dict()

    def __marshallable__(self):
        return self.data
