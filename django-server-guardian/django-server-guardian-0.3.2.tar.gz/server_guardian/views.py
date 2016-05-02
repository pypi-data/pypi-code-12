"""Views for the ``server_guardian`` app."""
import os
import subprocess

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View

from django_libs.views_mixins import JSONResponseMixin

from . import models
from .default_settings import DASHBOARD_VIEW_PERMISSION
from .management.commands.guardian_fetch import LOCKFILE


class GuardianDashboardView(ListView):
    """View that lists all servers and their status"""
    model = models.Server

    @method_decorator(user_passes_test(DASHBOARD_VIEW_PERMISSION))
    def dispatch(self, request, *args, **kwargs):
        return super(GuardianDashboardView, self).dispatch(
            request, *args, **kwargs)


class GuardianReloadView(JSONResponseMixin, View):
    """View, that allows reloading server status via ajax."""

    @method_decorator(user_passes_test(DASHBOARD_VIEW_PERMISSION))
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return redirect(reverse('server_guardian_dashboard'))
        return super(GuardianReloadView, self).dispatch(request, *args,
                                                        **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        ctx = {}
        if os.path.exists(LOCKFILE):
            # if lockfile exists, we know the command is still running
            ctx.update({
                'STATUS': 'running',
                'MESSAGE': 'Update command is still running. Please wait...',
            })
        elif self.request.method == 'GET':
            # GET requests are only to update the UI
            ctx.update({
                'STATUS': 'finished',
                'MESSAGE': 'Update command finished.',
            })
        elif self.request.method == 'POST':
            # POST requests are meant to start the command
            # if it is already running, the lockfile check above is fired
            status, message = self.start_command()
            ctx.update({'STATUS': status, 'MESSAGE': message})
        return ctx

    def start_command(self):

        # TODO not the most beautiful code, but it allows for easy reporting
        try:
            command = 'guardian_fetch'
            project_root = getattr(settings, 'DJANGO_PROJECT_ROOT')
            manage_py = os.path.join(project_root, 'manage.py')
            venv = os.environ.get('VIRTUAL_ENV', None)
            python = '/usr/bin/python'
            if venv is not None:
                python = os.path.join(venv, 'bin/python')
            popen_args = [python, manage_py, command]
            subprocess.Popen(popen_args)
        except Exception as ex:
            return 'error', (
                'There was an error while starting the update command:'
                ' {0}'.format(ex)
            )
        return 'started', 'Update command has been started. Please wait...'
