from __future__ import unicode_literals

import importlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.utils.http import base36_to_int
from django.views.generic.base import TemplateView

from .forms import OptOutForm


User = get_user_model()
FORM = getattr(settings, 'INVITER_FORM', 'inviter2.forms.RegistrationForm')
INVITER_FORM_USER_KWARG = getattr(
    settings, 'INVITER_FORM_USER_KWARG', 'instance'
)
INVITER_FORM_TEMPLATE = getattr(
    settings, 'INVITER_FORM_TEMPLATE', 'inviter2/register.html')
INVITER_DONE_TEMPLATE = getattr(
    settings, 'INVITER_DONE_TEMPLATE', 'inviter2/done.html')
INVITER_OPTOUT_TEMPLATE = getattr(
    settings, 'INVITER_OPTOUT_TEMPLATE', 'inviter2/opt-out.html')
INVITER_OPTOUT_DONE_TEMPLATE = getattr(
    settings, 'INVITER_OPTOUT_DONE_TEMPLATE', 'inviter2/opt-out-done.html')
TOKEN_GENERATOR = getattr(
    settings, 'INVITER_TOKEN_GENERATOR', 'inviter2.tokens.generator')


def import_attribute(path):
    """Import an attribute from a module."""
    module = '.'.join(path.split('.')[:-1])
    function = path.split('.')[-1]

    module = importlib.import_module(module)
    return getattr(module, function)


class UserMixin(object):
    """Handle retrieval of users from the token."""

    token_generator = import_attribute(TOKEN_GENERATOR)

    def get_user(self, uidb36):
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, OverflowError, User.DoesNotExist):
            raise Http404("No such invited user.")
        return user

    def dispatch(self, request, uidb36, token, *args, **kwargs):
        """
        Override the dispatch method to do token validation.

        If necessary this will deny access to the resource.

        Also passes the user as first argument after the request argument
        to the handler method.
        """
        assert uidb36 is not None and token is not None
        user = self.get_user(uidb36)

        if not self.token_generator.check_token(user, token):
            return HttpResponseForbidden()

        return super(UserMixin, self).dispatch(request, user, *args, **kwargs)


class Register(UserMixin, TemplateView):
    """
    A registration view for invited users.

    The user model already exists - this view just takes care of setting a
    password and username, and maybe update the email address. Anywho - one
    can customize the form that is used.
    """

    template_name = INVITER_FORM_TEMPLATE
    form = import_attribute(FORM)

    @property
    def redirect_url(self):
        return getattr(settings, 'INVITER_REDIRECT', 'inviter2:done')

    def get(self, request, user):
        context = {
            'invitee': user,
            'form': self.form(**{INVITER_FORM_USER_KWARG: user})
        }
        return self.render_to_response(context)

    def post(self, request, user):
        form = self.form(**{
            INVITER_FORM_USER_KWARG: user,
            'data': request.POST
        })

        if form.is_valid():
            form.save()
            try:
                return HttpResponseRedirect(reverse(self.redirect_url))
            except:
                return HttpResponseRedirect(self.redirect_url)
        return self.render_to_response({'invitee': user, 'form': form})


class Done(TemplateView):
    template_name = INVITER_DONE_TEMPLATE

    def get(self, request):
        return self.render_to_response({})


class OptOut(UserMixin, TemplateView):
    """
    Give the user also the option to *not* receive any invitations anymore.

    Which is happening in this view and :class:`inviter2.forms.OptOutForm`.
    """

    template_name = INVITER_OPTOUT_TEMPLATE

    def get(self, request, user):
        form = OptOutForm(instance=user)
        return self.render_to_response({'form': form})

    def post(self, request, user):
        form = OptOutForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('inviter2:opt-out-done'))
        return self.render_to_response({'form': form})


class OptOutDone(TemplateView):
    template_name = INVITER_OPTOUT_DONE_TEMPLATE

    def get(self, request):
        return self.render_to_response({})
