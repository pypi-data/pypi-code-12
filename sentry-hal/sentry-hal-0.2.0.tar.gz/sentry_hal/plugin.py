import socket
import json
import logging

from django import forms
from django.conf import settings
from sentry.plugins import Plugin
from sentry.plugins.bases.notify import NotificationPlugin, NotificationConfigurationForm
import sentry_hal

log = logging.getLogger(__name__)


class HALConfigurationForm(NotificationConfigurationForm):
    host = forms.CharField(label='Host', required=False, help_text='host')
    port = forms.IntegerField(label='Port', required=False, help_text='port')
    channel = forms.CharField(label='Channel', required=False, help_text='channel')


class HALMessage(Plugin):
    title = 'HAL'
    conf_key = 'hal'
    slug = 'hal'
    version = sentry_hal.VERSION
    author = 'Smarkets'
    author_url = 'http://www.github.com/smarkets/sentry-hal'
    project_conf_form = HALConfigurationForm

    def is_configured(self, project):
        return all(self.get_option(k, project) for k in ('host', 'port', 'channel'))

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        if not is_new or not self.is_configured(event.project):
            return
        link = '%s/sentry/%s/group/%d/' % (settings.SENTRY_URL_PREFIX, group.project.slug,
                                    group.id)
        message = '[sentry %s] %s (%s)' % (event.server_name, event.message, link)
        self.send_payload(event.project, message)

    def resolve_address_host(self, address):
        assert len(address) == 2, address
        return (socket.gethostbyname(address[0]), address[1])

    def send_payload(self, project, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = self.resolve_address_host((self.get_option('host', project), int(self.get_option('port', project))))
        payload = json.dumps(dict(message=message, room=self.get_option('channel', project))).encode()
        bytes_sent = sock.sendto(payload, address)
        if bytes_sent != len(payload):
            log.warn('Sent %s bytes instead of %s. Payload: %s', bytes_sent, len(payload), payload)
