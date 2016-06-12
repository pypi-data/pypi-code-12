from .base import BaseView


class DetailView(BaseView):

    def dispatch_request(self, **kwargs):
        stmt = self.get_query(**kwargs)
        item = stmt.first()
        self.append_context('item', item)
        return self.render()