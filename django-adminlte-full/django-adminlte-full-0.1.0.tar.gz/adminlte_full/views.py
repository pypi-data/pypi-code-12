from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _


class BaseView(TemplateView):
    __instance = None

    @classmethod
    def replace_with(cls, instance):
        cls.__instance = instance

    @classmethod
    def instance(cls):
        return cls.__instance or cls


class MessageView(BaseView):
    template_name = 'adminlte_full/base-layout.html'

    def get(self, request, *args, **kwargs):
        messages.debug(request, 'Redefine this page')
        return render(request, self.template_name)


class NotificationView(BaseView):
    template_name = 'adminlte_full/base-layout.html'

    def get(self, request, *args, **kwargs):
        messages.debug(request, 'Redefine this page')
        return render(request, self.template_name)


class TaskView(BaseView):
    template_name = 'adminlte_full/base-layout.html'

    def get(self, request, *args, **kwargs):
        messages.debug(request, 'Redefine this page')
        return render(request, self.template_name)


def index(request):
    pass


@login_required
def password_change_done(request,
                         template_name='registration/password_change_done.html',
                         extra_context=None):

    messages.success(request, _('Password change successful'))
    # {% _('Your password was changed.') %}

    # context = {
    #     'title': _('Password change successful'),
    # }
    # if extra_context is not None:
    #     context.update(extra_context)
    #
    # return TemplateResponse(request, template_name, context)
