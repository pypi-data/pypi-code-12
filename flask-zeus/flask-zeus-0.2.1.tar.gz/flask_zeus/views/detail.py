from .base import BaseView


class DetailView(BaseView):

    def dispatch_request(self, **kwargs):
        item = self.get_item(**kwargs)
        self.append_context('item', item)
        return self.render()
