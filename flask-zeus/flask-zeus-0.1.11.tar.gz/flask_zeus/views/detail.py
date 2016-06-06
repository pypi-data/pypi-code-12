from .base import BaseView


class DetailView(BaseView):

    def dispatch_request(self, **kwargs):
        stmt = self.get_query(**kwargs)
        item = stmt.first()
        context = self.get_context()
        context.update({
            'item': item
        })
        return self.render(**context)