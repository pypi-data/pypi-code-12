from django.shortcuts import render
from django.views.generic import TemplateView


class MessageView(TemplateView):
    template_name = 'adminlte_full/base-layout.html'

    def get_all_messages(self):
        raise NotImplementedError(
            'The method "get_all_messages" the abstract and should be implemented.'
        )

    def get(self, request, *args, **kwargs):
        messages = self
        return render(request, self.template_name, {'messages': messages})


class NotificationView(TemplateView):
    template_name = 'adminlte_full/base-layout.html'


class TaskView(TemplateView):
    template_name = 'adminlte_full/base-layout.html'


def index(request):
    pass