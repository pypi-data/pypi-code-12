"""Models for the server_guardian app."""
import json

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import constants


def get_parsed_response(response):
    """Parses the complete response of a server from json."""
    try:
        response = json.loads(response)
    except ValueError:
        response = constants.HTML_STATUS_FALLBACK
    if type(response) != list:
        response = constants.HTML_STATUS_FALLBACK
    return response


@python_2_unicode_compatible
class Server(models.Model):
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_('server name'),
    )
    url = models.URLField(
        verbose_name=_('API URL'),
        help_text='The URL, that the guardian API is available under.'
    )
    token = models.CharField(
        max_length=256,
        verbose_name=_('token'),
        help_text=(
            'Add this to your client server settings as'
            ' "SERVER_GUARDIAN_SECURITY_TOKEN".'
        ),
    )
    last_updated = models.DateTimeField(
        verbose_name=_('last updated'),
        blank=True, null=True,
    )
    log_age = models.PositiveIntegerField(
        verbose_name=_('log age'),
        help_text=_('How many days the logs are kept. Set to 0 for infinite.'),
        default=10,
    )

    def __str__(self):  # pragma: no cover
        if self.name:
            return self.name
        else:
            return self.url

    def get_absolute_url(self):
        return reverse('server_guardian_dashboard')

    def get_latest_log(self):
        return self.server_logs.all()[:10]


@python_2_unicode_compatible
class ServerLog(models.Model):
    """Stores logging information for a server."""
    content = models.TextField(
        verbose_name=_('content'),
        blank=True,
    )
    server = models.ForeignKey(
        Server,
        verbose_name=_('server'),
        related_name='server_logs',
    )
    time_logged = models.DateTimeField(
        verbose_name=_('time_logged'),
        auto_now=True,
    )
    status = models.CharField(
        verbose_name=_('status'),
        choices=constants.SERVER_STATUS_CHOICES,
        max_length=16,
    )
    status_code = models.CharField(
        verbose_name=_('status code'),
        max_length=3,
    )
    label = models.CharField(
        verbose_name=_('label'),
        max_length=512,
    )

    class Meta:
        ordering = ('server', 'label', '-time_logged')

    def __str__(self):  # pragma: no cover
        return '[{0}] {1} ({2})'.format(
            self.server, self.label, self.time_logged
        )

    def get_previous(self):
        try:
            return self._meta.model.objects.filter(
                label=self.label,
                server=self.server,
                time_logged__lt=self.time_logged,
            )[0]
        except IndexError:
            return self._meta.model(
                status_code=200,
                status=constants.SERVER_STATUS['OK'],
                label=self.label,
                server=self.server,
                content='No previous entry',
            )

    def has_errors(self):
        return self.status in constants.ERROR_STATUS

