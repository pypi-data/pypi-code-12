from .base import BaseView


class ListView(BaseView):

    def dispatch_request(self, **kwargs):
        pagination = self.get_pagination(**kwargs)
        self.append_context('items', pagination.items)
        self.append_context('pagination', pagination)
        return self.render()
